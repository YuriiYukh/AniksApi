from telethon import TelegramClient
from telethon.sessions import StringSession

from core.settings import settings


tg_client = TelegramClient(
    StringSession(settings.SESSION_STRING),
    settings.AP_ID,
    settings.API_HASH,
)
