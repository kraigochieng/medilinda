from fastapi_pagination import Page, Params
from fastapi_pagination.ext.sqlalchemy import paginate
from server.basemodels.sms import SMSMessageTypeEnum
from server.models.sms import SMSMessageModel
from sqlalchemy import desc, select
from sqlalchemy.orm import Session


class SMSMessageRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all(
        self, sms_type: SMSMessageTypeEnum | None = None, adr_id: str | None = None
    ) -> Page[SMSMessageModel]:
        stmt = select(SMSMessageModel)

        if sms_type:
            stmt = stmt.filter(SMSMessageModel.sms_type == sms_type)

        if adr_id:
            stmt = stmt.filter(SMSMessageModel.adr_id == adr_id)

        stmt = stmt.order_by(desc(SMSMessageModel.created_at))

        return paginate(self.db, stmt, params=Params(page=1, size=50))

    def get_by_id(self, id: str) -> SMSMessageModel | None:
        stmt = select(SMSMessageModel).where(SMSMessageModel.id == id)

        return self.db.scalar(stmt)

    def create(self, data: dict) -> SMSMessageModel:
        sms = SMSMessageModel(**data)

        self.db.add(sms)
        self.db.commit()
        self.db.refresh(sms)

        return sms

    def delete(self, id: str) -> bool:
        sms = self.get_by_id(id)

        if not sms:
            return False

        self.db.delete(sms)
        self.db.commit()

        return True
