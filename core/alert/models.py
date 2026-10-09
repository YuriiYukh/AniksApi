from pydantic import BaseModel


class KyivAlertResponse(BaseModel):
    """
    Model for response from the alerts api for Kyiv.
    Contains the alert status for Kyiv and Oblast, with details if there is some.
    """

    status_code: int
    is_kyiv_alert: bool
    kyiv_details: dict
    is_kyiv_oblast_alert: bool
    oblast_details: dict
