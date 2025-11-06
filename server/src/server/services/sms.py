from fastapi import HTTPException, status
from fastapi_pagination import Page, Params
from sqlalchemy.orm import Session, joinedload

from server.basemodels.sms import (
    SMSCountResponse,
    SMSMessageGetResponse,
    SMSMessageTypeEnum,
)
from server.clients.sms import AfricasTalkingClient
from server.models.adverse_drug_reaction_report import ADRModel
from server.models.medical_institution import (
    MedicalInstitutionModel,
)
from server.models.sms import SMSMessageModel


class SMSMessageService:
    def __init__(self, db: Session, sms_client: AfricasTalkingClient):
        self.db = db
        self.client = sms_client

    def _get_adr_data_for_sms(self, adr_id: str) -> tuple[ADRModel, str]:
        """
        Fetches the ADR model and the first available telephone number.
        Raises HTTPException if data is not found.
        """
        # Efficiently query ADR, its institution, and the institution's phones
        adr_model = (
            self.db.query(ADRModel)
            .options(
                joinedload(ADRModel.medical_institution).joinedload(
                    MedicalInstitutionModel.telephones
                )
            )
            .filter(ADRModel.id == adr_id)
            .first()
        )

        if not adr_model:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"ADR with id {adr_id} not found.",
            )

        if not adr_model.medical_institution:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Medical institution for ADR {adr_id} not found.",
            )

        if not adr_model.medical_institution.telephones:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No telephone numbers found for medical institution {adr_model.medical_institution.name}.",
            )

    def _send_and_save(
        self,
        adr_id: str,
        message_content: str,
        message_type: SMSMessageTypeEnum,
        recipients: list[str],
    ) -> list[SMSMessageModel]:
        """
        Sends the SMS via the client and saves the results to the DB.
        """

        response = self.client.send(message_content, recipients)

        sms_messages = []

        for message in response.get("SMSMessageData").get("Recipients"):
            sms_message = SMSMessageModel(
                adr_id=adr_id,
                content=message_content,
                sms_type=message_type,
                cost=message.get("cost"),
                message_id=message.get("messageId"),
                message_parts=message.get("messageParts"),
                number=message.get("number"),
                status=message.get("status"),
                status_code=message.get("statusCode"),
            )
            sms_messages.append(sms_message)

        return self.repo.create_batch(sms_messages)

    def send_individual_alert(self, adr_id: str) -> list[SMSMessageModel]:
        adr_model, telephone = self._get_adr_data_for_sms(adr_id)

        message_content = (
            f"URGENT ADR ALERT: {adr_model.patient_name} at {adr_model.medical_institution.name} "
            f"has a causality assessment of CERTAIN. We are further investigating this as the Pharmacy and Poisons Board (PPB) for further guidance. Call +254795743049 for further information."
        )
        message_type = SMSMessageTypeEnum.individual_alert

        return self._send_and_save(
            adr_id=adr_id,
            message_content=message_content,
            message_type=message_type,
            recipients=[telephone],
        )

    def send_additional_info_request(self, adr_id: str) -> list[SMSMessageModel]:
        adr_model, telephone = self._get_adr_data_for_sms(adr_id)

        message_content = (
            f"ADR FOLLOW-UP: An ADR case involving {adr_model.patient_name} from {adr_model.medical_institution.name} requires additional clinical details. "
            f"Kindly review and submit supporting information to the Pharmacy and Poisons Board (PPB)."
        )
        message_type = SMSMessageTypeEnum.additional_info

        return self._send_and_save(
            adr_id=adr_id,
            message_content=message_content,
            message_type=message_type,
            recipients=[telephone],
        )

    def list_messages(
        self,
        pagination_params: Params,
        sms_type: SMSMessageTypeEnum | None = None,
        adr_id: str | None = None,
        
    ) -> Page[SMSMessageGetResponse]:
        return self.repo.get_all(sms_type=sms_type, adr_id=adr_id, pagination_params=pagination_params)

    def get_message_by_id(self, id: str) -> SMSMessageGetResponse | None:
        return self.repo.get_by_id(id)

    def get_paginated_sms_counts(
        self, pagination_params: Params, sms_type: SMSMessageTypeEnum | None
    ) -> Page[SMSCountResponse]:
        """
        Gets paginated, grouped SMS counts.
        """
        return self.repo.get_sms_counts_by_adr(pagination_params=pagination_params, sms_type=sms_type)

    def create_message(self, sms_data: dict) -> SMSMessageGetResponse:
        return self.repo.create(sms_data)

    def delete_message(self, id: str) -> bool:
        return self.repo.delete(id)
