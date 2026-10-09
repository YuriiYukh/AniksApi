from fastapi import APIRouter, HTTPException, Depends, Request, status
from telethon import TelegramClient

from core.services import get_api_key
from core.telegram_client.models import TgResponse
from core.telegram_client.services import get_messages_service
from core.telegram_client.dependencies import get_telegram_client
from core.limiter import limiter
from core.logger import get_logger

air_tg = APIRouter(prefix="/air_tg")
logger = get_logger(__name__)


@air_tg.get("/all", response_model=TgResponse, dependencies=[Depends(get_api_key)])
@limiter.limit("5/minute")
async def get_all_alerts(
    request: Request,
    client: TelegramClient = Depends(
        get_telegram_client,
    ),
):
    try:
        return await get_messages_service(client)
    except Exception as e:
        logger.error(f"Failed to gather Telegram messages: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unexpected error occurred.",
        )
