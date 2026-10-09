from fastapi import APIRouter, Request

from core.alert.models import KyivAlertResponse
from core.alert.services import get_kyiv_alert
from core.limiter import limiter


alerts_router = APIRouter(prefix="/alerts")


@alerts_router.get(
    "/kyiv",
    response_model=KyivAlertResponse,
)
@limiter.limit("10/minute")
async def kyiv_alerts(request: Request):
    """
    Endpoint to get an air raid alert statues and their details
    for Kyiv and Oblast.
    """
    alerts_info = await get_kyiv_alert()
    return alerts_info
