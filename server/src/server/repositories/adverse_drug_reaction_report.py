from fastapi_pagination import Page, Params
from fastapi_pagination.ext.sqlalchemy import paginate
from server.basemodels.adverse_drug_reaction_report import (
    ADRPostRequest,
    ReviewStatusFilter,
)
from server.exceptions import ResourceNotFoundError
from server.models.adverse_drug_reaction_report import ADRModel
from server.models.causality_assessment_level import (
    CausalityAssessmentLevelEnum,
    CausalityAssessmentLevelModel,
)
from server.models.review import ReviewModel
from server.models.user import UserModel
from sqlalchemy import and_, case, desc, false, func, or_, select, true
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

    def get_by_id(self, id: str) -> ADRModel:
        stmt = select(ADRModel).where(ADRModel.id == id)

        model = self.db.scalar(stmt)

        if not model:
            raise ResourceNotFoundError(f"ADR with id {id} not found")

        return model

    def get_paginated_adrs_with_reviews(
        self,
        pagination_params: Params,
        query: str | None,
        causality_level: CausalityAssessmentLevelEnum | None = None,
        review_status: ReviewStatusFilter | None = None,
    ) -> Page[ADRModel]:
        """
        Gets a paginated list of ADRs with their newest causality level
        and review counts. Search and filters run in the database, so the
        total and the pages stay correct.
        """
        search_term = f"%{query}%" if query else None

        # Main query using ROW_NUMBER and CTE for SQLite compatibility
        ranked_causality_cte = select(
            CausalityAssessmentLevelModel,
            func.row_number()
            .over(
                partition_by=CausalityAssessmentLevelModel.adr_id,
                order_by=[
                    CausalityAssessmentLevelModel.created_at.desc(),
                    CausalityAssessmentLevelModel.id.desc(),
                ],
            )
            .label("rn"),
        ).cte("ranked_causality")

        approved_count = func.count(case((ReviewModel.approved == true(), 1)))
        unapproved_count = func.count(case((ReviewModel.approved == false(), 1)))

        main_stmt = (
            select(
                ADRModel.id.label("adr_id"),
                ADRModel.patient_name,
                (UserModel.first_name + " " + UserModel.last_name).label("created_by"),
                ADRModel.created_at,
                ranked_causality_cte.c.causality_assessment_level_value,
                approved_count.label("approved_reviews"),
                unapproved_count.label("unapproved_reviews"),
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
                or_(
                    ADRModel.patient_name.ilike(search_term),
                    ADRModel.patient_address.ilike(search_term),
                    ADRModel.ward_or_clinic.ilike(search_term),
                    ADRModel.inpatient_or_outpatient_number.ilike(search_term),
                )
            )

        if causality_level is not None:
            main_stmt = main_stmt.where(
                ranked_causality_cte.c.causality_assessment_level_value
                == causality_level
            )

        has_assessment = ranked_causality_cte.c.id.is_not(None)
        if review_status == ReviewStatusFilter.needs_review:
            main_stmt = main_stmt.having(
                and_(has_assessment, approved_count + unapproved_count == 0)
            )
        elif review_status == ReviewStatusFilter.approved:
            main_stmt = main_stmt.having(approved_count > unapproved_count)
        elif review_status == ReviewStatusFilter.not_approved:
            main_stmt = main_stmt.having(
                and_(
                    approved_count + unapproved_count > 0,
                    approved_count <= unapproved_count,
                )
            )

        return paginate(self.db, main_stmt, params=pagination_params)

    def _save(self, model: ADRModel | None, commit: bool) -> None:
        """Commit, or only flush so the caller can finish a larger transaction."""
        if commit:
            self.db.commit()
        else:
            self.db.flush()
        if model is not None:
            self.db.refresh(model)

    def create(self, data: ADRPostRequest, commit: bool = True) -> ADRModel:
        model = ADRModel(**data.model_dump())

        self.db.add(model)
        self._save(model, commit)

        return model

    def update(self, id: str, data: ADRPostRequest, commit: bool = True) -> ADRModel:
        model = self.get_by_id(id)

        # The creator of a report never changes when someone else edits it.
        for key, value in data.model_dump(exclude={"user_id"}).items():
            setattr(model, key, value)

        self._save(model, commit)

        return model

    def delete(self, id: str, commit: bool = True) -> None:
        model = self.get_by_id(id)

        self.db.delete(model)
        self._save(None, commit)
