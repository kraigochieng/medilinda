from fastapi_pagination import Page, Params
from fastapi_pagination.ext.sqlalchemy import paginate
from server.models.adverse_drug_reaction_report import ADRModel
from server.models.causality_assessment_level import (
    CausalityAssessmentLevelEnum,
    CausalityAssessmentLevelModel,
)
from server.models.medical_institution import (
    MedicalInstitutionModel,
    MedicalInstitutionTelephoneModel,
)
from server.models.review import ReviewModel
from server.models.sms import SMSMessageModel
from server.utils.alerts import transform_alert_rows
from sqlalchemy import Select, and_, case, distinct, false, func, select, true
from sqlalchemy.orm import Session


class AlertRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_alerts_query(
        self,
        pagination_params: Params,
        search_term: str | None = None,
        causality_level: CausalityAssessmentLevelEnum | None = None,
        has_been_sent: bool | None = None,
    ) -> Page:
        """
        Builds the core SQLAlchemy query for fetching ADR alerts
        based on the provided filters.
        """
        approved_reviews = func.count(
            distinct(case((ReviewModel.approved == true(), ReviewModel.id)))
        )
        unapproved_reviews = func.count(
            distinct(case((ReviewModel.approved == false(), ReviewModel.id)))
        )
        sms_count_agg = func.count(distinct(SMSMessageModel.id))

        main_stmt = (
            select(
                ADRModel.id.label("adr_id"),
                ADRModel.patient_name.label("patient_name"),
                MedicalInstitutionModel.name.label("medical_institution_name"),
                MedicalInstitutionModel.mfl_code.label("medical_institution_mfl_code"),
                ADRModel.created_at.label("created_at"),
                func.group_concat(
                    distinct(MedicalInstitutionTelephoneModel.telephone)
                ).label("telephones"),
                sms_count_agg.label("sms_count"),
            )
            .select_from(ADRModel)
            .join(
                CausalityAssessmentLevelModel,
                ADRModel.id == CausalityAssessmentLevelModel.adr_id,
            )
            .join(
                MedicalInstitutionModel,
                ADRModel.medical_institution_id == MedicalInstitutionModel.id,
            )
            .join(
                MedicalInstitutionTelephoneModel,
                MedicalInstitutionModel.id
                == MedicalInstitutionTelephoneModel.medical_institution_id,
                isouter=True,
            )
            .join(
                ReviewModel,
                CausalityAssessmentLevelModel.id
                == ReviewModel.causality_assessment_level_id,
                isouter=True,
            )
            .join(SMSMessageModel, ADRModel.id == SMSMessageModel.adr_id, isouter=True)
            .group_by(
                ADRModel.id,
                ADRModel.patient_name,
                MedicalInstitutionModel.name,
                MedicalInstitutionModel.mfl_code,
                ADRModel.created_at,
            )
            .having(approved_reviews > unapproved_reviews)
            .order_by(ADRModel.created_at.desc())
        )

        # Apply WHERE filters
        where_conditions = []
        if search_term:
            where_conditions.append(
                func.lower(ADRModel.patient_name).like(func.lower(search_term))
            )
        if causality_level:
            where_conditions.append(
                CausalityAssessmentLevelModel.causality_assessment_level_value
                == causality_level
            )
        if where_conditions:
            main_stmt = main_stmt.where(and_(*where_conditions))

        # Apply HAVING filters
        having_conditions = []
        if has_been_sent is True:
            having_conditions.append(sms_count_agg != 0)
        elif has_been_sent is False:
            having_conditions.append(sms_count_agg == 0)

        if having_conditions:
            main_stmt = main_stmt.having(and_(*having_conditions))

        return paginate(
            self.db,
            main_stmt,
            params=pagination_params,
            transformer=transform_alert_rows,
        )
