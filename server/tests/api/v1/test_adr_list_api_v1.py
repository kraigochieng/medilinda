from unittest.mock import Mock

import pytest
from fastapi import status
from server.api.v1.endpoints.adverse_drug_reaction_reports_details import (
    get_adverse_drug_reaction_report_service,
)
from server.main import app
from server.models.causality_assessment_level import (
    CausalityAssessmentLevelEnum,
    CausalityAssessmentLevelModel,
)
from server.repositories.adverse_drug_reaction_report import (
    AdverseDrugReactionReportRepository,
)
from server.services.adverse_drug_reaction_report import (
    AdverseDrugReactionReportService,
)

URL = "/api/v1/adrs-details/with-causality-and-review-count"


@pytest.fixture(autouse=True)
def service(client, db):
    svc = AdverseDrugReactionReportService(
        db=db, ml_model=Mock(), encoder=Mock(), explainer=Mock()
    )
    app.dependency_overrides[get_adverse_drug_reaction_report_service] = lambda: svc


@pytest.fixture
def two_adrs(db, sample_adverse_drug_reaction_report_post_request):
    repo = AdverseDrugReactionReportRepository(db)
    t = sample_adverse_drug_reaction_report_post_request
    for name, level in [
        ("Alice", CausalityAssessmentLevelEnum.likely),
        ("Bob", CausalityAssessmentLevelEnum.certain),
    ]:
        adr = repo.create(data=t.model_copy(update={"patient_name": name}))
        db.add(
            CausalityAssessmentLevelModel(
                adr_id=adr.id, causality_assessment_level_value=level
            )
        )
    db.commit()


def names(response):
    return {item["patient_name"] for item in response.json()["items"]}


def test_lists_everything_without_filters(client, two_adrs):
    response = client.get(URL)

    assert response.status_code == status.HTTP_200_OK
    assert names(response) == {"Alice", "Bob"}


def test_filters_by_causality_level(client, two_adrs):
    assert names(client.get(URL, params={"causality_level": "certain"})) == {"Bob"}


def test_filters_by_review_status(client, two_adrs):
    response = client.get(URL, params={"review_status": "needs_review"})
    assert names(response) == {"Alice", "Bob"}  # neither has a review yet

    response = client.get(URL, params={"review_status": "approved"})
    assert names(response) == set()


def test_searches_by_text(client, two_adrs):
    assert names(client.get(URL, params={"query": "ali"})) == {"Alice"}


@pytest.mark.parametrize(
    "params",
    [{"causality_level": "bogus"}, {"review_status": "bogus"}],
)
def test_rejects_unknown_filter_values(client, two_adrs, params):
    assert client.get(URL, params=params).status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
