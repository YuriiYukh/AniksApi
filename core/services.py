"""
Main router utils and services
"""

from fastapi import Security, HTTPException, status
from fastapi.security import APIKeyHeader

from speedtest import Speedtest
from core.models import SpeedtestResponse
from core.settings import settings


ROUND = 2


api_key_header = APIKeyHeader(name="X-API-Key", auto_error=True)


def get_api_key(api_key_header: str = Security(api_key_header)):
    if api_key_header not in settings.API_KEYS:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key.",
        )
    return api_key_header


def speed_test(in_bytes: bool = False) -> SpeedtestResponse:
    """Main speedtest function"""
    convert_divisor = 10**6 * (8 if in_bytes else 1)

    client = Speedtest()
    down_speed = round(client.download() / convert_divisor, ROUND)
    up_speed = round(client.upload() / convert_divisor, ROUND)
    ping = client.results.ping

    return SpeedtestResponse(down_speed=down_speed, up_speed=up_speed, ping=ping)
