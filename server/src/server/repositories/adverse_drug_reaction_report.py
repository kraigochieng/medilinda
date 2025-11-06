from fastapi_pagination import Page, Params
from fastapi_pagination.ext.sqlalchemy import paginate
from server.basemodels.adverse_drug_reaction_report import ADRPostRequest
from server.models.adverse_drug_reaction_report import ADRModel
from server.models.causality_assessment_level import CausalityAssessmentLevelModel
from server.models.review import ReviewModel
from server.models.user import UserModel
from sqlalchemy import and_, case, desc, false, func, select, true
from sqlalchemy.orm import Session


class AdverseDrugReactionReportRepository:
    def __init__(self, db: Session):
        self.db = db

    def get(self, query: str | None, pagination_params: Params) -> Page[ADRModel]:
        stmt = select(ADRModel)

        if query:
            stmt.filter(
                ADRModel.patient_name.ilike(f"%{query}%")
                | ADRModel.patient_address.ilike(f"%{query}%")
                | ADRModel.inpatient_or_outpatient_number.ilike(f"%{query}%")
                | ADRModel.ward_or_clinic.ilike(f"%{query}%")
            )

        stmt.order_by(desc(ADRModel.created_at))

        return paginate(self.db, stmt, params=pagination_params)

    def get_by_id(self, id: str) -> ADRModel | None:
        stmt = select(ADRModel).where(ADRModel.id == id)

        return self.db.scalar(stmt)

    def get_paginated_adrs_with_reviews(
        self, pagination_params: Params, query: str | None
    ) -> Page[ADRModel]:
        """
        Gets a paginated list of ADRs with their first causality level
        and review counts.
        """
        search_term = f"%{query}%" if query else None

        # Main query using ROW_NUMBER and CTE for SQLite compatibility
        ranked_causality_cte = select(
            CausalityAssessmentLevelModel,
            func.row_number()
            .over(
                partition_by=CausalityAssessmentLevelModel.adr_id,
                order_by=CausalityAssessmentLevelModel.created_at.asc(),
            )
            .label("rn"),
        ).cte("ranked_causality")

        main_stmt = (
            select(
                ADRModel.id.label("adr_id"),
                ADRModel.patient_name,
                (UserModel.first_name + " " + UserModel.last_name).label("created_by"),
                ADRModel.created_at,
                ranked_causality_cte.c.causality_assessment_level_value,
                func.count(case((ReviewModel.approved == true(), 1))).label(
                    "approved_reviews"
                ),
                func.count(case((ReviewModel.approved == false(), 1))).label(
                    "unapproved_reviews"
                ),
            )
            .select_from(ADRModel)
            .join(UserModel, ADRModel.user_id == UserModel.id)
            .join(
                ranked_causality_cte,
                and_(
                    ranked_causality_cte.c.adr_id == ADRModel.id,
                    ranked_causality_cte.c.rn == 1,
                ),
                isouter=True,
            )
            .join(
                ReviewModel,
                ReviewModel.causality_assessment_level_id == ranked_causality_cte.c.id,
                isouter=True,
            )
            .group_by(
                ADRModel.id,
                ADRModel.patient_name,
                UserModel.first_name,
                UserModel.last_name,
                ranked_causality_cte.c.causality_assessment_level_value,
            )
            .order_by(ADRModel.created_at.desc())
        )

        if search_term:
            main_stmt = main_stmt.where(
                func.lower(ADRModel.patient_name).like(func.lower(search_term))
            )

        return paginate(self.db, main_stmt, params=pagination_params)

    def create(self, data: ADRPostRequest) -> ADRModel:
        model = ADRModel(**data.model_dump())

        self.db.add(model)
        self.db.commit()
        self.db.refresh(model)

        return model

    def update(self, id: str, data: ADRPostRequest) -> ADRModel | None:
        model = self.get_by_id(id)

        if not model:
            return None

        for key, value in data.model_dump().items():
            setattr(model, key, value)

        self.db.commit()
        self.db.refresh(model)

        return model

    def delete(self, id: str) -> bool:
        model = self.get_by_id(id)

        if not model:
            return False

        self.db.delete(model)
        self.db.commit()

        return True
