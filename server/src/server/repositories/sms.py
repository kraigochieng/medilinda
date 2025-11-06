from fastapi_pagination import Page, Params
from fastapi_pagination.ext.sqlalchemy import paginate
from server.basemodels.sms import SMSCountResponse, SMSMessageTypeEnum
from server.models.adverse_drug_reaction_report import ADRModel
from server.models.medical_institution import MedicalInstitutionModel
from server.models.sms import SMSMessageModel
from sqlalchemy import desc, func, select
from sqlalchemy.orm import Session


class SMSMessageRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all(
        self,
        pagination_params: Params,
        sms_type: SMSMessageTypeEnum | None = None,
        adr_id: str | None = None,
    ) -> Page[SMSMessageModel]:
        stmt = select(SMSMessageModel)

        if sms_type:
            stmt = stmt.filter(SMSMessageModel.sms_type == sms_type)

        if adr_id:
            stmt = stmt.filter(SMSMessageModel.adr_id == adr_id)

        stmt = stmt.order_by(desc(SMSMessageModel.created_at))

        return paginate(self.db, stmt, params=pagination_params)

    def get_by_id(self, id: str) -> SMSMessageModel | None:
        stmt = select(SMSMessageModel).where(SMSMessageModel.id == id)

        return self.db.scalar(stmt)

    def get_sms_counts_by_adr(
        self, pagination_params: Params, sms_type: SMSMessageTypeEnum | None
    ) -> Page[SMSCountResponse]:
        """
        Gets a paginated, grouped count of SMS messages by ADR,
        including medical institution details.
        """

        main_stmt = (
            select(
                SMSMessageModel.adr_id,
                SMSMessageModel.sms_type,
                MedicalInstitutionModel.mfl_code.label("medical_institution_mfl_code"),
                MedicalInstitutionModel.name.label("medical_institution_name"),
                ADRModel.patient_name.label("patient_name"),
                func.count(SMSMessageModel.id).label("sms_count"),
            )
            .join(
                ADRModel,
                ADRModel.id == SMSMessageModel.adr_id,
            )
            .join(
                MedicalInstitutionModel,
                MedicalInstitutionModel.id == ADRModel.medical_institution_id,
            )
            .group_by(
                SMSMessageModel.adr_id,
                SMSMessageModel.sms_type,
                MedicalInstitutionModel.name,
                MedicalInstitutionModel.mfl_code,
                ADRModel.patient_name,
            )
            .order_by(desc(ADRModel.patient_name))
        )

        # Apply filter if provided
        if sms_type:
            main_stmt = main_stmt.filter(SMSMessageModel.sms_type == sms_type)

        return paginate(self.db, main_stmt, params=pagination_params)

    def create(self, data: dict) -> SMSMessageModel:
        sms = SMSMessageModel(**data)

        self.db.add(sms)
        self.db.commit()
        self.db.refresh(sms)

        return sms

    def create_batch(
        self, sms_messages: list[SMSMessageModel]
    ) -> list[SMSMessageModel]:
        """
        Adds a list of SMSMessageModel instances to the session,
        commits, and refreshes them.
        """
        self.db.add_all(sms_messages)
        self.db.commit()
        for msg in sms_messages:
            self.db.refresh(msg)
        return sms_messages

    def delete(self, id: str) -> bool:
        sms = self.get_by_id(id)

        if not sms:
            return False

        self.db.delete(sms)
        self.db.commit()

        return True
