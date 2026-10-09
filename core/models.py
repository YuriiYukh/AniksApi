"""
Main app models.
"""

from pydantic import BaseModel


class HelloResponse(BaseModel):
    message: str


class SpeedtestResponse(BaseModel):
    down_speed: float
    up_speed: float
    ping: float
