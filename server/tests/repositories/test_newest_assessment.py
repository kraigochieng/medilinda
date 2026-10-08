"""An ADR can have several causality assessments over time (one per edit that
changes a model input). Only the newest one counts in lists, alerts and charts;
older ones, and the reviews given on them, are history."""

import datetime

import pytest
from fastapi_pagination import Params
from server.models.causality_assessment_level import (
    CausalityAssessmentLevelEnum,
    CausalityAssessmentLevelModel,
)
from server.models.review import ReviewModel
from server.repositories.adverse_drug_reaction_report import (
    AdverseDrugReactionReportRepository,
)
from server.repositories.alerts import AlertRepository
from server.repositories.dashboard import DashboardRepository

PARAMS = Params(page=1, size=20)
OLD = datetime.datetime(2025, 1, 1, 9, 0, 0)
NEW = datetime.datetime(2025, 1, 2, 9, 0, 0)


def add_assessment(db, adr, value, created_at):
    cal = CausalityAssessmentLevelModel(
        adr_id=adr.id,
        causality_assessment_level_value=value,
        created_at=created_at,
    )
    db.add(cal)
    db.commit()
    return cal


def add_review(db, cal, user, approved):
    db.add(
        ReviewModel(
            causality_assessment_level_id=cal.id, user_id=user.id, approved=approved
        )
    )
    db.commit()


@pytest.fixture
def adr(db, sample_adverse_drug_reaction_report_post_request):
    return AdverseDrugReactionReportRepository(db).create(
        data=sample_adverse_drug_reaction_report_post_request
    )


@pytest.fixture
def edited_adr(db, adr, test_user):
    """Reviewed and approved as 'possible', then edited: now 'likely', unreviewed."""
    old = add_assessment(db, adr, CausalityAssessmentLevelEnum.possible, OLD)
    add_review(db, old, test_user, approved=True)
    add_assessment(db, adr, CausalityAssessmentLevelEnum.likely, NEW)
    return adr


def test_list_shows_the_newest_assessment_and_its_reviews(db, edited_adr):
    page = AdverseDrugReactionReportRepository(db).get_paginated_adrs_with_reviews(
        pagination_params=PARAMS, query=None
    )

    (row,) = page.items
    assert row.causality_assessment_level_value == CausalityAssessmentLevelEnum.likely
    assert (row.approved_reviews, row.unapproved_reviews) == (0, 0)


def test_alerts_ignore_approvals_given_on_an_older_assessment(db, edited_adr):
    page = AlertRepository(db).get_alerts_query(pagination_params=PARAMS)

    assert page.items == []


def test_alerts_include_an_adr_whose_newest_assessment_is_approved(
    db, edited_adr, test_user
):
    newest = (
        db.query(CausalityAssessmentLevelModel)
        .filter_by(adr_id=edited_adr.id, causality_assessment_level_value="likely")
        .one()
    )
    add_review(db, newest, test_user, approved=True)

    page = AlertRepository(db).get_alerts_query(pagination_params=PARAMS)

    assert len(page.items) == 1


def test_causality_distribution_counts_each_adr_once(db, edited_adr):
    rows = DashboardRepository(db).get_causality_distribution()

    assert [(r[0].value, r[1]) for r in rows] == [("likely", 1)]


def test_reviewed_counts_use_the_newest_assessment(db, edited_adr):
    result = DashboardRepository(db).get_reviewed_counts()

    assert result.total_adrs == 1
    assert result.reviewed_adrs == 0  # the old review does not count


def test_approval_status_only_looks_at_the_newest_assessment(db, edited_adr):
    assert DashboardRepository(db).get_approval_status() == []


def test_approval_status_counts_a_reviewed_newest_assessment(db, edited_adr, test_user):
    newest = (
        db.query(CausalityAssessmentLevelModel)
        .filter_by(adr_id=edited_adr.id, causality_assessment_level_value="likely")
        .one()
    )
    add_review(db, newest, test_user, approved=True)

    rows = DashboardRepository(db).get_approval_status()

    assert [(r[0], r[1]) for r in rows] == [("Approved", 1)]
