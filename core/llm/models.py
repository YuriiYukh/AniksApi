from datetime import datetime

from pydantic import BaseModel, Field

from core.llm.enums import DangerAlerts


class LLMRequest(BaseModel):
    title: str
    content: str
    created_at: datetime = Field(default_factory=datetime.now)


class AirRaidStatus(BaseModel):
    danger: DangerAlerts
    details: str


class ChatOverview(BaseModel):
    is_interesting: bool
    details: str
