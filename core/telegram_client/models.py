from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class TgResponse(BaseModel):
    """
    Response for the last and recent messages lists from Telegram.
    """

    timedelta_messages: list[dict[str, str]]
    last_messages: list[dict[str, str]]
    created_at: datetime = Field(default_factory=datetime.now)


class TgMsgList(BaseModel):
    """
    Response for list of messages from a Telegram chat.
    """

    messages: list[dict[str, Any]]
    created_at: datetime = Field(default_factory=datetime.now)
