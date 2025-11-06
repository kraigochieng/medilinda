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


@pytest.fixture
def sample_medical_institution_post_request(db: Session) -> MedicalInstitutionModel:
    """Fixture to create a sample medical institution in the database."""
    institution = MedicalInstitutionModel(
        name="Test Hospital",
        mfl_code="MFL999",
    )

    db.add(institution)
    db.commit()
    db.refresh(institution)

    return institution


@pytest.fixture
def sample_adverse_drug_reaction_report_post_request(
    test_user: UserModel,
    sample_medical_institution_post_request: MedicalInstitutionModel,
) -> ADRPostRequest:
    """Fixture for creating a sample ADRPostRequest."""
    return ADRPostRequest(
        medical_institution_id=sample_medical_institution_post_request.id,
        user_id=test_user.id,
        # Personal Details
        patient_name="Jane Smith",
        inpatient_or_outpatient_number="OP-123456",
        patient_age=45.0,
        patient_date_of_birth=date(1980, 5, 10),
        patient_address="123 Kijabe Street, Nairobi",
        patient_weight_kg=68.5,
        patient_height_cm=165.0,
        ward_or_clinic="TB Clinic A",
        patient_gender=GenderEnum.female,
        pregnancy_status=PregnancyStatusEnum.not_pregnant,
        known_allergy=KnownAllergyEnum.yes,
        # Suspected Adverse Reaction
        date_of_onset_of_reaction=date(2025, 10, 15),
        description_of_reaction="Severe rash, jaundice (yellowing of skin and eyes), and elevated liver enzymes.",
        # --- Medicine fields ---
        rifampicin_suspected=True,
        rifampicin_start_date=date(2025, 10, 1),
        rifampicin_stop_date=date(2025, 10, 16),
        rifampicin_dose_amount=600.0,
        rifampicin_frequency_number=1.0,
        rifampicin_route="Oral",
        rifampicin_batch_no="RF-BATCH-001",
        rifampicin_manufacturer="Kenya Medical Supplies",
        isoniazid_suspected=True,
        isoniazid_start_date=date(2025, 10, 1),
        isoniazid_stop_date=date(2025, 10, 16),
        isoniazid_dose_amount=300.0,
        isoniazid_frequency_number=1.0,
        isoniazid_route="Oral",
        isoniazid_batch_no="IZ-BATCH-002",
        isoniazid_manufacturer="Kenya Medical Supplies",
        pyrazinamide_suspected=False,
        pyrazinamide_start_date=date(2025, 10, 1),
        pyrazinamide_stop_date=None,
        pyrazinamide_dose_amount=1500.0,
        pyrazinamide_frequency_number=1.0,
        pyrazinamide_route="Oral",
        ethambutol_suspected=False,
        ethambutol_start_date=date(2025, 10, 1),
        ethambutol_stop_date=None,
        ethambutol_dose_amount=800.0,
        ethambutol_frequency_number=1.0,
        ethambutol_route="Oral",
        # Rechallenge/Dechallenge
        rechallenge=RechallengeEnum.no,
        dechallenge=DechallengeEnum.yes,
        # Grading of Reaction/Event
        severity=SeverityEnum.severe,
        is_serious=IsSeriousEnum.yes,
        criteria_for_seriousness=CriteriaForSeriousnessEnum.hospitalisation,
        action_taken=ActionTakenEnum.drug_withdrawn,
        outcome=OutcomeEnum.recovering,
        comments="Patient has a known allergy to penicillin. LFTs on 15/10/2025 showed ALT 450 U/L, AST 380 U/L, Total Bili 4.5 mg/dL. Patient admitted for monitoring.",
    )


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

    # 2. Create CAL 1 (the first/oldest one)
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

    # 4. Create Reviews linked to CAL 1 (the one that should be picked)
    review1 = ReviewModel(
        causality_assessment_level_id=cal1.id, user_id=test_user.id, approved=True
    )
    review2 = ReviewModel(
        causality_assessment_level_id=cal1.id, user_id=test_user.id, approved=False
    )
    # 5. Create a Review linked to CAL 2 (this one should be ignored by the query)
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

    # Should pick the value from the *first* CAL (cal1)
    assert (
        item.causality_assessment_level_value
        == CausalityAssessmentLevelEnum.unclassified
    )
    # Should count *only* reviews for cal1
    assert item.approved_reviews == 1
    assert item.unapproved_reviews == 1


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
