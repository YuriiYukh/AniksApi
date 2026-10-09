import httpx
from core.alert.models import KyivAlertResponse
from core.logger import get_logger
from core.settings import settings

from fastapi import HTTPException, status

logger = get_logger(__name__)

base_url = "https://api.alerts.in.ua/v1/alerts"
active_alert_url = f"{base_url}/active.json"

headers = {"Authorization": f"Bearer {settings.ALERTS_TOKEN}"}


async def get_kyiv_alert() -> KyivAlertResponse:
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            kyiv_alert = {}
            kyiv_oblast_alert = {}
            response = await client.get(active_alert_url, headers=headers)
            response.raise_for_status()

            for item in response.json()["alerts"]:
                if "київська область" in item["location_oblast"].lower():
                    kyiv_oblast_alert.update(
                        {
                            "location_oblast": item["location_oblast"],
                            "notes": item["notes"],
                            "started_at": item["started_at"],
                        }
                    )
                elif "київ" in item["location_oblast"].lower():
                    kyiv_alert.update(
                        {
                            "location_oblast": item["location_oblast"],
                            "notes": item["notes"],
                            "started_at": item["started_at"],
                        }
                    )
            return KyivAlertResponse(
                status_code=response.status_code,
                is_kyiv_alert=bool(kyiv_alert),
                kyiv_details=kyiv_alert,
                is_kyiv_oblast_alert=bool(kyiv_oblast_alert),
                oblast_details=kyiv_oblast_alert,
            )

        except httpx.HTTPStatusError as e:
            logger.error(f"Alerts API returned an error: {e}")
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Alerts API returned an error.",
            )
        except httpx.RequestError as e:
            logger.error(f"Failed to connect to Alerts API: {e}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Failed to connect to Alerts API.",
            )
