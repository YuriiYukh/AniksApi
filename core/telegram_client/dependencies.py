from telethon import TelegramClient

from core.telegram_client.client import tg_client


def get_telegram_client() -> TelegramClient:
    return tg_client
