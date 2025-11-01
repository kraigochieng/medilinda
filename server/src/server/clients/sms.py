import logging
from typing import Any

import africastalking
from fastapi import HTTPException, status
from server.settings import settings


class AfricasTalkingClient:
    """
    A client to handle interactions with the Africa's Talking API.
    """

    def __init__(self, username: str, api_key: str):
        try:
            africastalking.initialize(username, api_key)
            self.sms = africastalking.SMS
        except Exception as e:
            logging.error(f"Failed to initialize Africa's Talking: {e}")
            self.sms = None

    def send(self, message: str, recipients: list[str]) -> dict[str, Any]:
        """
        Sends an SMS message.

        Raises:
            HTTPException: If the client failed to initialize or the send fails.
        """
        if self.sms is None:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="SMS service is not initialized.",
            )

        try:
            response = self.sms.send(message, recipients)

            if (
                "SMSMessageData" not in response
                or "Recipients" not in response["SMSMessageData"]
            ):
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Invalid response from SMS provider: {response}",
                )

            return response

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Failed to send SMS via provider: {str(e)}",
            )


def get_sms_client() -> AfricasTalkingClient:
    """
    Dependency injector for the AfricasTalkingClient.
    """
    return AfricasTalkingClient(
        username=settings.africas_talking_username,
        api_key=settings.africas_talking_api_key,
    )
