import datetime

import pytest
from fastapi_pagination import Params
from server.basemodels.adverse_drug_reaction_report import (
    ReviewStatusFilter,
    SortField,
    SortOrder,
)
from server.models.causality_assessment_level import (
    CausalityAssessmentLevelEnum,
    CausalityAssessmentLevelModel,
)
from server.models.review import ReviewModel
from server.repositories.adverse_drug_reaction_report import (
    AdverseDrugReactionReportRepository,
)

Level = CausalityAssessmentLevelEnum
PARAMS = Params(page=1, size=50)
T0 = datetime.datetime(2025, 1, 1, 9, 0, 0)


@pytest.fixture
def repo(db):
    return AdverseDrugReactionReportRepository(db)


def make_adr(repo, template, db, name, level, approvals=(), **overrides):
    """An ADR with one assessment and reviews with the given approvals."""
    adr = repo.create(
        data=template.model_copy(update={"patient_name": name, **overrides})
    )
    if level is not None:
        cal = CausalityAssessmentLevelModel(
            adr_id=adr.id, causality_assessment_level_value=level, created_at=T0
        )
        db.add(cal)
        db.commit()
        for approved in approvals:
            db.add(
                ReviewModel(
                    causality_assessment_level_id=cal.id,
                    user_id=template.user_id,
                    approved=approved,
                )
            )
        db.commit()
    return adr


@pytest.fixture
def adrs(db, repo, sample_adverse_drug_reaction_report_post_request):
    t = sample_adverse_drug_reaction_report_post_request
    return {
        "needs_review": make_adr(repo, t, db, "Needs Review", Level.likely),
        "approved": make_adr(repo, t, db, "Approved One", Level.certain, [True, True, False]),
        "not_approved": make_adr(repo, t, db, "Not Approved", Level.possible, [False]),
        "tied": make_adr(repo, t, db, "Tied Votes", Level.likely, [True, False]),
        "no_assessment": make_adr(repo, t, db, "No Assessment", None),
    }


def names(repo, **filters):
    page = repo.get_paginated_adrs_with_reviews(
        pagination_params=PARAMS, query=filters.pop("query", None), **filters
    )
    return {row.patient_name for row in page.items}


def test_no_filter_returns_everything(repo, adrs):
    assert len(names(repo)) == 5


def test_filter_by_causality_level(repo, adrs):
    assert names(repo, causality_level=[Level.likely]) == {"Needs Review", "Tied Votes"}
    assert names(repo, causality_level=[Level.certain]) == {"Approved One"}
    assert names(repo, causality_level=[Level.unlikely]) == set()


def test_needs_review_means_an_assessment_with_no_reviews(repo, adrs):
    assert names(repo, review_status=[ReviewStatusFilter.needs_review]) == {"Needs Review"}


def test_approved_means_more_approvals_than_rejections(repo, adrs):
    assert names(repo, review_status=[ReviewStatusFilter.approved]) == {"Approved One"}


def test_not_approved_means_reviewed_but_not_approved(repo, adrs):
    assert names(repo, review_status=[ReviewStatusFilter.not_approved]) == {
        "Not Approved",
        "Tied Votes",
    }


def test_filters_combine(repo, adrs):
    result = names(
        repo,
        causality_level=[Level.likely],
        review_status=[ReviewStatusFilter.not_approved],
    )
    assert result == {"Tied Votes"}


def test_the_total_matches_the_filter_so_paging_stays_correct(repo, adrs):
    page = repo.get_paginated_adrs_with_reviews(
        pagination_params=Params(page=1, size=1),
        query=None,
        review_status=[ReviewStatusFilter.not_approved],
    )
    assert page.total == 2
    assert len(page.items) == 1


@pytest.mark.parametrize(
    "field,value,expected",
    [
        ("patient_name", "needs rev", "Needs Review"),
        ("patient_address", "Mombasa Road", "Approved One"),
        ("ward_or_clinic", "Ward 7", "Not Approved"),
        ("inpatient_or_outpatient_number", "IP-998", "Tied Votes"),
    ],
)
def test_search_covers_patient_address_ward_and_number(
    db, repo, sample_adverse_drug_reaction_report_post_request, field, value, expected
):
    t = sample_adverse_drug_reaction_report_post_request
    for name in ["Needs Review", "Approved One", "Not Approved", "Tied Votes"]:
        overrides = {
            "patient_address": f"Addr {name}",
            "ward_or_clinic": f"W {name}",
            "inpatient_or_outpatient_number": f"N {name}",
        }
        if name == expected and field != "patient_name":
            overrides[field] = value
        make_adr(repo, t, db, name, Level.likely, **overrides)
    # The searched value is stored on exactly one ADR (or, for the name, in its name).
    assert names(repo, query=value) == {expected}


def test_search_is_case_insensitive_and_can_be_combined_with_filters(
    db, repo, sample_adverse_drug_reaction_report_post_request
):
    t = sample_adverse_drug_reaction_report_post_request
    make_adr(repo, t, db, "Alice Wanjiru", Level.likely)
    make_adr(repo, t, db, "Alice Otieno", Level.certain)

    assert names(repo, query="ALICE") == {"Alice Wanjiru", "Alice Otieno"}
    assert names(repo, query="alice", causality_level=[Level.certain]) == {"Alice Otieno"}


# --- Several values for one filter, and sorting ------------------------------------


def test_several_causality_levels_match_any_of_them(repo, adrs):
    assert names(repo, causality_level=[Level.certain, Level.possible]) == {
        "Approved One",
        "Not Approved",
    }


def test_several_review_statuses_match_any_of_them(repo, adrs):
    assert names(
        repo,
        review_status=[ReviewStatusFilter.needs_review, ReviewStatusFilter.approved],
    ) == {"Needs Review", "Approved One"}


def test_several_values_in_one_filter_still_combine_with_the_other_filter(repo, adrs):
    result = names(
        repo,
        causality_level=[Level.likely, Level.certain],
        review_status=[ReviewStatusFilter.approved, ReviewStatusFilter.not_approved],
    )
    assert result == {"Approved One", "Tied Votes"}


def test_an_empty_list_is_no_filter(repo, adrs):
    assert len(names(repo, causality_level=[], review_status=[])) == 5


def ordered(repo, **kw):
    page = repo.get_paginated_adrs_with_reviews(
        pagination_params=PARAMS, query=None, **kw
    )
    return [row.patient_name for row in page.items]


def test_sort_by_patient_name(repo, adrs):
    assert ordered(repo, sort_by=SortField.patient_name, sort_order=SortOrder.asc) == [
        "Approved One",
        "Needs Review",
        "No Assessment",
        "Not Approved",
        "Tied Votes",
    ]
    assert ordered(repo, sort_by=SortField.patient_name, sort_order=SortOrder.desc)[0] == (
        "Tied Votes"
    )


def test_sort_by_causality_puts_the_most_certain_first_when_descending(repo, adrs):
    result = ordered(repo, sort_by=SortField.causality_level, sort_order=SortOrder.desc)

    assert result[0] == "Approved One"  # certain
    assert set(result[1:3]) == {"Needs Review", "Tied Votes"}  # likely
    assert result[3] == "Not Approved"  # possible
    assert result[-1] == "No Assessment"  # none


def test_sort_by_causality_ascending_starts_with_the_least_certain(repo, adrs):
    result = ordered(repo, sort_by=SortField.causality_level, sort_order=SortOrder.asc)

    assert result[0] == "Not Approved"  # possible
    assert result[3] == "Approved One"  # certain
    assert result[-1] == "No Assessment"


def test_a_report_without_an_assessment_sorts_last_both_ways(repo, adrs):
    for order in (SortOrder.asc, SortOrder.desc):
        result = ordered(repo, sort_by=SortField.causality_level, sort_order=order)
        assert result[-1] == "No Assessment"


def test_the_default_order_is_newest_first(repo, adrs):
    assert ordered(repo) == ordered(
        repo, sort_by=SortField.created_at, sort_order=SortOrder.desc
    )


def test_sorting_keeps_paging_stable(repo, adrs):
    seen = []
    for page_number in (1, 2, 3):
        page = repo.get_paginated_adrs_with_reviews(
            pagination_params=Params(page=page_number, size=2),
            query=None,
            sort_by=SortField.patient_name,
            sort_order=SortOrder.asc,
        )
        seen += [row.patient_name for row in page.items]

    assert seen == sorted(seen) and len(seen) == 5
