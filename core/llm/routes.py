from typing import Annotated

from fastapi import APIRouter, HTTPException, Depends, Request, status

from pydantic import BaseModel

from litellm import acompletion, exceptions
from cachetools import TTLCache
from telethon import TelegramClient

from core.llm.enums import SupportedLLMs
from core.llm.models import AirRaidStatus, ChatOverview
from core.llm.prompts import JOKE_PROMPT, format_message, RecipePrompt
from core.llm.services import analyse_air_situation, analyse_chat_discussions
from core.llm.utils import clear_llm_response_text
from core.services import get_api_key
from core.limiter import limiter
from core.telegram_client.dependencies import get_telegram_client
from core.logger import get_logger

LLM_router = APIRouter(prefix="/llms")
cache = TTLCache(maxsize=2, ttl=60)
logger = get_logger(__name__)


class ExistingLLMsResponse(BaseModel):
    message: list[str]


@LLM_router.get(
    "/all", response_model=ExistingLLMsResponse, dependencies=[Depends(get_api_key)]
)
@limiter.limit("2/minute")
async def existing_llms(request: Request):
    """
    Get currently supported LLMs.
    """
    return {"message": [llm.value for llm in SupportedLLMs]}


class JokeResponse(BaseModel):
    message: str


@LLM_router.post(
    "/joke", response_model=JokeResponse, dependencies=[Depends(get_api_key)]
)
@limiter.limit("2/minute")
async def generate_joke(request: Request):
    """
    Submit a request to the LLM to get a short joke.
    """
    try:
        messages = format_message("user", JOKE_PROMPT)
        response = await acompletion(
            model=SupportedLLMs.GEMINI3_LITE.value, messages=messages
        )

        if not response.choices or not response.choices[0].message.content:
            raise HTTPException(
                status_code=status.HTTP_504_GATEWAY_TIMEOUT,
                detail="LLM returned an empty response.",
            )

        return {"message": clear_llm_response_text(response.choices[0].message.content)}
    except HTTPException:
        raise
    except exceptions.APIError as e:
        logger.error(f"Litellm API error: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Litellm API error.",
        )
    except Exception as e:
        logger.error(f"Unexpected error occurred: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unexpected error occurred.",
        )


class RecipeResponse(BaseModel):
    message: str


@LLM_router.post(
    "/recipe", response_model=RecipeResponse, dependencies=[Depends(get_api_key)]
)
@limiter.limit("1/minute")
async def recipe_by_ingredients(request: Request, ingredients: list[str]):
    """
    Submit a request to the LLM to get a recipe by a list of ingredients.
    Need to provide list of ingredients.
    """
    messages = format_message("user", RecipePrompt.get_ingredients_prompt(ingredients))
    try:
        response = await acompletion(
            model=SupportedLLMs.GEMINI3_LITE.value, messages=messages
        )
        if not response.choices or not response.choices[0].message.content:
            raise HTTPException(
                status_code=status.HTTP_504_GATEWAY_TIMEOUT,
                detail="LLM returned an empty response.",
            )

        return {"message": response.choices[0].message.content}
    except HTTPException:
        raise
    except exceptions.APIError as e:
        logger.error(f"Litellm api error: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Litellm api error.",
        )
    except Exception as e:
        logger.error(f"Unexpected error occurred: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unexpected error occurred.",
        )


@LLM_router.get(
    "/danger-kyiv",
    dependencies=[Depends(get_api_key)],
    response_model=AirRaidStatus,
)
@limiter.limit("1/second")
async def analyse_air_danger(
    request: Request, client: Annotated[TelegramClient, Depends(get_telegram_client)]
):
    """
    Returns the current danger status for Kyiv, Ukraine.
    """
    if "status" in cache:
        return cache["status"]
    try:
        result = await analyse_air_situation(client)
        cache["status"] = result

        return result

    except HTTPException:
        raise
    except (exceptions.RateLimitError, exceptions.ServiceUnavailableError) as e:
        logger.warning(f"LLM provider issue: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Gemini quota exhausted or the service is unavailable. Try again later.",
        )

    except Exception as e:
        logger.error(f"Internal server error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error occurred.",
        )


@LLM_router.get(
    "/chat-interest",
    dependencies=[Depends(get_api_key)],
    response_model=ChatOverview,
)
@limiter.limit("1/second")
async def analyse_chat_interest(
    request: Request, client: Annotated[TelegramClient, Depends(get_telegram_client)]
):
    """
    Returns info about last chat discussions and if they are interesting.
    """
    if "interest" in cache:
        return cache["interest"]
    try:
        result = await analyse_chat_discussions(client)
        cache["interest"] = result

        return result
    except HTTPException:
        raise
    except (exceptions.RateLimitError, exceptions.ServiceUnavailableError) as e:
        logger.warning(f"LLM provider issue: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Gemini quota exhausted or the service is unavailable. Try again later.",
        )

    except Exception as e:
        logger.error(f"Internal server error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error occurred.",
        )
