from typing import Annotated, TypeVar

from fastapi import Depends, HTTPException, status
from pydantic import BaseModel, ValidationError
from telethon import TelegramClient
from litellm import acompletion

from core.alert.services import get_kyiv_alert
from core.llm.enums import SupportedLLMs
from core.llm.models import AirRaidStatus, ChatOverview
from core.llm.prompts import AirRaidPrompt, ChatInterestPrompt, format_message
from core.logger import get_logger
from core.settings import settings
from core.telegram_client.dependencies import get_telegram_client
from core.telegram_client.services import get_messages_service, get_last_messages

logger = get_logger(__name__)

ModelT = TypeVar("ModelT", bound=BaseModel)


def _parse_llm_response(response, model: type[ModelT]) -> ModelT:
    """
    Validates the LLM structured output against the given Pydantic model.
    """
    if not response.choices or not response.choices[0].message.content:
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="LLM returned an empty response.",
        )
    try:
        return model.model_validate_json(response.choices[0].message.content)
    except ValidationError as e:
        logger.error(f"LLM returned an invalid {model.__name__}: {e}")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="LLM returned an invalid response.",
        )


async def analyse_air_situation(
    client: Annotated[TelegramClient, Depends(get_telegram_client)],
) -> AirRaidStatus:
    """
    Function to analyse the air raid alerts based on the alerts API
    and telegram messages via LLM.
    """

    tg_data = await get_messages_service(client)
    data_for_llm = tg_data.model_dump_json()
    tg_failed = not tg_data.timedelta_messages and not tg_data.last_messages

    try:
        alerts_for_llm = (await get_kyiv_alert()).model_dump_json()
        alerts_failed = False
    except HTTPException:
        alerts_for_llm = '{"error": "Alerts API is unavailable."}'
        alerts_failed = True

    if alerts_failed and tg_failed:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Both Telegram API and alert status API are unavailable. Try again later.",
        )

    messages = format_message(
        "user",
        AirRaidPrompt.get_air_raid_prompt(
            data_for_llm,
            alerts_for_llm,
        ),
    )

    response = await acompletion(
        model=SupportedLLMs.GEMINI3_LITE.value,
        messages=messages,
        response_format=AirRaidStatus,
        temperature=0.7,
        num_retries=3,
    )
    return _parse_llm_response(response, AirRaidStatus)


async def analyse_chat_discussions(
    client: Annotated[TelegramClient, Depends(get_telegram_client)],
) -> ChatOverview:
    """
    Function to get a discussions from the last chat in telegram
    and analyse if there is something interesting.
    """
    if not settings.CHAT_DIGEST_CHAT_NAME_PREFIX:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Chat digest is not configured.",
        )

    tg_data = await get_last_messages(client, settings.CHAT_DIGEST_CHAT_NAME_PREFIX)
    if not tg_data.messages:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No messages found in the configured chat.",
        )

    data_for_llm = tg_data.model_dump(mode="json")

    messages = format_message(
        "user",
        ChatInterestPrompt.get_interest_prompt(
            data_for_llm,
            topics=settings.CHAT_DIGEST_TOPICS,
            extra_instructions=settings.CHAT_DIGEST_EXTRA_INSTRUCTIONS,
        ),
    )
    response = await acompletion(
        model=SupportedLLMs.GEMINI3_LITE.value,
        messages=messages,
        response_format=ChatOverview,
        temperature=0.5,
        num_retries=3,
    )
    return _parse_llm_response(response, ChatOverview)
