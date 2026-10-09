import datetime
import pytz

from telethon import TelegramClient

from core.logger import get_logger
from core.telegram_client.models import TgResponse, TgMsgList

logger = get_logger(__name__)

LAST_MESSAGES_LIMIT_QUANTITY = 7
LAST_MESSAGES_LIMIT_TIMEDELTA_MINS = 5

channels_to_gather = {"@war_monitor", "@vanek_nikolaev", "@kpszsu"}
words_whitelist = {
    "бпла",
    "мопед",
    "громко",
    "ціль",
    "швидкісна",
    "спуск",
    "безпілотник",
    "обстановка",
    "баллистика",
    "крылатой",
    "крылатая",
    "баллистическая",
    "минус",
    "дорозвідка",
    "без фіксації",
    "не фіксується",
    "тривога",
    "відбій",
    "отбой",
}


def _filter_message(message: str) -> bool:
    return any(word in message for word in words_whitelist)


def _format_channel_messages(messages: list, channel_name: str) -> tuple[list, list]:
    five_mins_ago = datetime.datetime.now(pytz.utc) - datetime.timedelta(
        minutes=LAST_MESSAGES_LIMIT_TIMEDELTA_MINS
    )
    timedelta_messages = []
    last_messages = []
    for message in messages:
        if not _filter_message(message.message.lower()):
            continue
        formatted_time = message.date.strftime("%d.%m.%Y, %H:%M:%S")
        formatted_message = {
            "channel": channel_name,
            "datetime": formatted_time,
            "text": message.message,
        }
        if message.date > five_mins_ago:
            timedelta_messages.append(formatted_message)
        last_messages.append(formatted_message)

    return timedelta_messages, last_messages


async def get_messages_service(client: TelegramClient) -> TgResponse:
    timedelta_messages = []
    last_messages = []
    for channel_name in channels_to_gather:
        try:
            channel = await client.get_entity(channel_name)
            messages = await client.get_messages(
                channel, limit=LAST_MESSAGES_LIMIT_QUANTITY
            )
            timedelta, last = _format_channel_messages(messages, channel_name)
            timedelta_messages.extend(timedelta)
            last_messages.extend(last)

        except AttributeError as e:
            logger.error(e)

    return TgResponse(
        timedelta_messages=timedelta_messages, last_messages=last_messages
    )


async def get_last_messages(
    client: TelegramClient, channel_name_start: str
) -> TgMsgList:
    entity = None
    async for dialog in client.iter_dialogs():
        if dialog.name.startswith(channel_name_start):
            entity = dialog.entity
            break

    if entity is None:
        logger.error(f"No chat starting with '{channel_name_start}' found among dialogs.")
        return TgMsgList(messages=[])

    raw_messages = await client.get_messages(entity, limit=100)
    messages = []
    for m in raw_messages:
        text = getattr(m, "message", None)
        if not text:
            continue
        sender = getattr(m, "sender", None)
        sender_name = getattr(sender, "username", None) or getattr(
            sender, "first_name", None
        )
        messages.append(
            {
                "id": m.id,
                "date": m.date,
                "text": text,
                "sender_id": m.sender_id,
                "sender_name": sender_name,
            }
        )

    return TgMsgList(messages=messages)
