from typing import List, Optional

from fastapi import HTTPException, status

from server.basemodels.sms import SMSMessageTypeEnum
from server.repositories.sms_message import SMSMessageRepository


class SMSMessageService:
    """Business logic for SMS message operations."""

    def __init__(self, repo: SMSMessageRepository):
        self.repo = repo

    def list_messages(
        self,
        sms_type: Optional[SMSMessageTypeEnum] = None,
        adr_id: Optional[str] = None,
    ):
        if sms_type:
            return self.repo.get_by_type(sms_type)
        if adr_id:
            return self.repo.get_by_adr_id(adr_id)
        return self.repo.get_all()

    def get_message_by_id(self, sms_id: str):
        sms = self.repo.get_by_id(sms_id)
        if not sms:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="SMS Message not found",
            )
        return sms

    def create_message(self, sms_data: dict):
        return self.repo.create(sms_data)

    def delete_message(self, sms_id: str):
        deleted = self.repo.delete(sms_id)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="SMS Message not found",
            )
        return {"message": "SMS Message deleted successfully"}
