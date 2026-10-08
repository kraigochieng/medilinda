from server.models.causality_assessment_level import CausalityAssessmentLevelModel
from sqlalchemy import and_, exists, or_, select
from sqlalchemy.orm import aliased


def newest_assessment_ids():
    """Ids of the newest causality assessment of each ADR.

    An ADR gets a new assessment whenever an edit changes a model input. Older
    ones, and the reviews given on them, are history, so lists, alerts and
    charts must only look at the newest. Use as
    `CausalityAssessmentLevelModel.id.in_(newest_assessment_ids())`.
    """
    cal = CausalityAssessmentLevelModel
    newer = aliased(CausalityAssessmentLevelModel)

    return select(cal.id).where(
        ~exists().where(
            newer.adr_id == cal.adr_id,
            or_(
                newer.created_at > cal.created_at,
                and_(newer.created_at == cal.created_at, newer.id > cal.id),
            ),
        )
    )


# The same rule as raw SQL, for the queries written as text.
NEWEST_ASSESSMENT_SQL = """
    NOT EXISTS (
        SELECT 1 FROM causality_assessment_level newer
        WHERE newer.adr_id = cal.adr_id
          AND (newer.created_at > cal.created_at
               OR (newer.created_at = cal.created_at AND newer.id > cal.id))
    )
"""
