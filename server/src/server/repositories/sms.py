from fastapi_pagination import Page, Params
from fastapi_pagination.ext.sqlalchemy import paginate
from server.basemodels.sms import SMSMessageTypeEnum
from server.models.sms import SMSMessageModel
from sqlalchemy import desc, select
from sqlalchemy.orm import Session


class SMSMessageRepository:
    """Handles all direct DB operations related to SMS messages."""

    def __init__(self, db: Session):
        self.db = db

    def get_all(self) -> Page[SMSMessageModel]:
        stmt = select(SMSMessageModel).order_by(desc(SMSMessageModel.created_at))

        return paginate(self.db, stmt, params=Params(page=1, size=50))

    def get_by_type(self, sms_type: SMSMessageTypeEnum) -> Page[SMSMessageModel]:
        stmt = (
            select(SMSMessageModel)
            .where(SMSMessageModel.sms_type == sms_type)
            .order_by(desc(SMSMessageModel.created_at))
        )

        return paginate(self.db, stmt, params=Params(page=1, size=50))

    def get_by_adr_id(self, adr_id: str) -> Page[SMSMessageModel]:
        stmt = (
            select(SMSMessageModel)
            .where(SMSMessageModel.adr_id == adr_id)
            .order_by(desc(SMSMessageModel.created_at))
        )

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
