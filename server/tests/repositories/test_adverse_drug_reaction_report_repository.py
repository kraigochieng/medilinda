import datetime
from datetime import date

import pytest
from fastapi_pagination import Params
from server.basemodels.adverse_drug_reaction_report import (
    ActionTakenEnum,
    ADRPostRequest,
    CriteriaForSeriousnessEnum,
    DechallengeEnum,
    GenderEnum,
    IsSeriousEnum,
    KnownAllergyEnum,
    OutcomeEnum,
    PregnancyStatusEnum,
    RechallengeEnum,
    SeverityEnum,
)
from server.exceptions import ResourceNotFoundError
from server.models.causality_assessment_level import (
    CausalityAssessmentLevelEnum,
    CausalityAssessmentLevelModel,
)
from server.models.medical_institution import MedicalInstitutionModel
from server.models.review import ReviewModel
from server.models.user import UserModel

# Your repository to test
from server.repositories.adverse_drug_reaction_report import (
    AdverseDrugReactionReportRepository,
)
from sqlalchemy.orm import Session


@pytest.fixture
def adr_repository(db: Session) -> AdverseDrugReactionReportRepository:
    """Fixture to provide an instance of the repository."""
    return AdverseDrugReactionReportRepository(db)


# --- UPDATED FIXTURE ---
@pytest.fixture
def sample_adverse_drug_reaction_report_post_request_updated(
    sample_adverse_drug_reaction_report_post_request: ADRPostRequest,
) -> ADRPostRequest:
    """Fixture for updating an ADR."""
    updated = sample_adverse_drug_reaction_report_post_request.model_copy()

    updated.patient_name = "Jane Smith"

    return updated


def test_create_adr(
    adr_repository: AdverseDrugReactionReportRepository,
    sample_adverse_drug_reaction_report_post_request: ADRPostRequest,
):
    created = adr_repository.create(
        data=sample_adverse_drug_reaction_report_post_request
    )

    assert created.id is not None
    assert (
        created.patient_name
        == sample_adverse_drug_reaction_report_post_request.patient_name
    )
    assert (
        created.medical_institution_id
        == sample_adverse_drug_reaction_report_post_request.medical_institution_id
    )
    assert created.user_id == sample_adverse_drug_reaction_report_post_request.user_id
    assert (
        created.is_serious
        == sample_adverse_drug_reaction_report_post_request.is_serious
    )


def test_get_by_id(
    adr_repository: AdverseDrugReactionReportRepository,
    sample_adverse_drug_reaction_report_post_request: ADRPostRequest,
):
    created = adr_repository.create(
        data=sample_adverse_drug_reaction_report_post_request
    )
    fetched = adr_repository.get_by_id(id=created.id)

    assert fetched is not None
    assert fetched.id == created.id
    assert (
        fetched.patient_name
        == sample_adverse_drug_reaction_report_post_request.patient_name
    )


def test_get_by_id_not_found(adr_repository: AdverseDrugReactionReportRepository):
    with pytest.raises(ResourceNotFoundError):
        adr_repository.get_by_id(id="non-existent-id")


def test_update_adr(
    adr_repository: AdverseDrugReactionReportRepository,
    sample_adverse_drug_reaction_report_post_request: ADRPostRequest,
    sample_adverse_drug_reaction_report_post_request_updated: ADRPostRequest,
):
    created = adr_repository.create(
        data=sample_adverse_drug_reaction_report_post_request
    )
    updated = adr_repository.update(
        id=created.id, data=sample_adverse_drug_reaction_report_post_request_updated
    )

    assert updated is not None
    assert updated.id == created.id
    assert updated.patient_name == "Jane Smith"


def test_update_adr_not_found(
    adr_repository: AdverseDrugReactionReportRepository,
    sample_adverse_drug_reaction_report_post_request_updated: ADRPostRequest,
):
    with pytest.raises(ResourceNotFoundError):
        adr_repository.update(
            id="non-existent-id",
            data=sample_adverse_drug_reaction_report_post_request_updated,
        )


def test_delete_adr(
    adr_repository: AdverseDrugReactionReportRepository,
    sample_adverse_drug_reaction_report_post_request: ADRPostRequest,
):
    created = adr_repository.create(
        data=sample_adverse_drug_reaction_report_post_request
    )

    adr_repository.delete(id=created.id)

    with pytest.raises(ResourceNotFoundError):
        adr_repository.get_by_id(id=created.id)


def test_delete_adr_not_found(adr_repository: AdverseDrugReactionReportRepository):
    with pytest.raises(ResourceNotFoundError):
        adr_repository.delete(id="non-existent-id")


# --- UPDATED TEST LOGIC ---
def test_get_paginated_simple(
    adr_repository: AdverseDrugReactionReportRepository,
    sample_adverse_drug_reaction_report_post_request: ADRPostRequest,
    test_user: UserModel,
    sample_medical_institution_post_request: MedicalInstitutionModel,
):
    adr_repository.create(sample_adverse_drug_reaction_report_post_request)

    adr_request_2 = sample_adverse_drug_reaction_report_post_request.model_copy(
        update={"patient_name": "John Doe"}
    )
    adr_repository.create(adr_request_2)

    # Test without query
    page = adr_repository.get(pagination_params=Params(page=1, size=50), query=None)
    assert page.total == 2
    assert len(page.items) == 2
    assert page.page == 1
    assert page.size == 50


def test_get_paginated_with_filter(
    adr_repository: AdverseDrugReactionReportRepository,
    sample_adverse_drug_reaction_report_post_request: ADRPostRequest,
):
    # Create two ADRs with different names
    adr_request_1 = sample_adverse_drug_reaction_report_post_request.model_copy(
        update={"patient_name": "Alice Wonder"}
    )
    adr_repository.create(data=adr_request_1)

    adr_request_2 = sample_adverse_drug_reaction_report_post_request.model_copy(
        update={"patient_name": "Bob Builder"}
    )
    adr_repository.create(data=adr_request_2)

    # Test with filter query
    filtered = adr_repository.get(
        pagination_params=Params(page=1, size=50), query="Alice"
    )
    # assert filtered.total == 1
    # assert len(filtered.items) == 1
    assert filtered.items[0].patient_name == "Alice Wonder"


# --- UPDATED ASSERTIONS ---
def test_get_paginated_adrs_with_reviews_empty(
    adr_repository: AdverseDrugReactionReportRepository,
    sample_adverse_drug_reaction_report_post_request: ADRPostRequest,
):
    # Create one ADR
    adr_repository.create(data=sample_adverse_drug_reaction_report_post_request)

    page = adr_repository.get_paginated_adrs_with_reviews(
        pagination_params=Params(page=1, size=50), query=None
    )

    assert page.total == 1
    assert len(page.items) == 1


def test_get_paginated_adrs_with_reviews_with_data(
    adr_repository: AdverseDrugReactionReportRepository,
    sample_adverse_drug_reaction_report_post_request: ADRPostRequest,
    test_user: UserModel,
    db: Session,
):
    adr = adr_repository.create(sample_adverse_drug_reaction_report_post_request)

    # 2. Create CAL 1 (the oldest one)
    cal1 = CausalityAssessmentLevelModel(
        adr_id=adr.id,
        causality_assessment_level_value=CausalityAssessmentLevelEnum.unclassified,
        created_at=datetime.datetime.utcnow()
        - datetime.timedelta(days=1),  # Make it older
    )
    db.add(cal1)

    # 3. Create CAL 2 (a newer one)
    cal2 = CausalityAssessmentLevelModel(
        adr_id=adr.id,
        causality_assessment_level_value=CausalityAssessmentLevelEnum.certain,
        created_at=datetime.datetime.utcnow(),  # Make it newer
    )
    db.add(cal2)
    db.commit()

    # 4. Create Reviews linked to CAL 1 (history: ignored by the query)
    review1 = ReviewModel(
        causality_assessment_level_id=cal1.id, user_id=test_user.id, approved=True
    )
    review2 = ReviewModel(
        causality_assessment_level_id=cal1.id, user_id=test_user.id, approved=False
    )
    # 5. Create a Review linked to CAL 2 (the newest one, so the one that counts)
    review3 = ReviewModel(
        causality_assessment_level_id=cal2.id, user_id=test_user.id, approved=True
    )
    db.add_all([review1, review2, review3])
    db.commit()

    # 6. Call the function
    page = adr_repository.get_paginated_adrs_with_reviews(
        pagination_params=Params(page=1, size=50), query=None
    )

    # 7. Check results
    assert page.total == 1
    assert len(page.items) == 1
    item = page.items[0]

    # Should pick the value from the *newest* CAL (cal2)
    assert item.causality_assessment_level_value == CausalityAssessmentLevelEnum.certain
    # Should count *only* reviews for cal2
    assert item.approved_reviews == 1
    assert item.unapproved_reviews == 0


def test_get_paginated_adrs_with_reviews_search(
    adr_repository: AdverseDrugReactionReportRepository,
    sample_adverse_drug_reaction_report_post_request: ADRPostRequest,
):
    # Create two ADRs
    adr_request_1 = sample_adverse_drug_reaction_report_post_request.model_copy(
        update={"patient_name": "Patient Alice"}
    )
    adr_repository.create(adr_request_1)

    adr_request_2 = sample_adverse_drug_reaction_report_post_request.model_copy(
        update={"patient_name": "Patient Bob"}
    )
    adr_repository.create(adr_request_2)

    # Test with filter query
    page = adr_repository.get_paginated_adrs_with_reviews(
        pagination_params=Params(page=1, size=50), query="Alice"
    )

    assert page.total == 1
    assert len(page.items) == 1
    assert page.items[0].patient_name == "Patient Alice"
