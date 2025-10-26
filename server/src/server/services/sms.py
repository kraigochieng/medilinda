from server.basemodels.sms import SMSMessageGetResponse, SMSMessageTypeEnum
from server.repositories.sms import SMSMessageRepository
from fastapi_pagination import Page


class SMSMessageService:
    def __init__(self, repo: SMSMessageRepository):
        self.repo = repo

    def list_messages(
        self,
        sms_type: SMSMessageTypeEnum | None = None,
        adr_id: str | None = None,
    ) -> Page[SMSMessageGetResponse]:
        return self.repo.get_all(sms_type=sms_type, adr_id=adr_id)

    def get_message_by_id(self, id: str) -> SMSMessageGetResponse | None:
        return self.repo.get_by_id(id)

    def create_message(self, sms_data: dict) -> SMSMessageGetResponse:
        return self.repo.create(sms_data)

    def delete_message(self, id: str) -> bool:
        return self.repo.delete(id)
