import os

os.environ.setdefault("BETTER_AUTH_URL", "http://localhost:3000")
os.environ.setdefault("BETTER_AUTH_INTERNAL_SECRET", "test-internal-secret")

from contextlib import asynccontextmanager
from datetime import date

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
from server.models.medical_institution import MedicalInstitutionModel

import pytest
from fastapi.testclient import TestClient
from fastapi_pagination import add_pagination
from server.db.base import Base
from server.dependencies import get_db
from server.main import app
from server.models.user import UserModel
from server.repositories.review import ReviewRepository
from server.utils.audit import unbind_actor
from server.utils.auth import get_current_active_user

from tests.db import TestSessionLocal, test_engine
from tests.dependencies import override_get_current_active_user


@asynccontextmanager
async def no_lifespan(app):
    yield


@pytest.fixture(autouse=True)
def reset_audit_actor():
    """The audit actor lives in a context variable, so clear it after each test."""
    yield
    unbind_actor()


@pytest.fixture(scope="function")
def db():
    Base.metadata.create_all(bind=test_engine)
    session = TestSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=test_engine)


@pytest.fixture(scope="function")
def client(db):
    def override_get_db():
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_active_user] = override_get_current_active_user

    app.router.lifespan_context = no_lifespan
    add_pagination(app)

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def anon_client(db):
    """A client with the real auth dependency (nothing overridden) and no lifespan."""

    def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db
    app.router.lifespan_context = no_lifespan
    add_pagination(app)

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()


@pytest.fixture
def review_repository(db):
    return ReviewRepository(db)


@pytest.fixture
def test_user(db):
    user = UserModel(
        id="user-1",
        username="testuser",
        password="testuser",
        first_name="Test",
        last_name="User",
        disabled=False,
    )

    db.add(user)
    db.commit()
    db.refresh(user)
    
    return user


@pytest.fixture
def sample_medical_institution_post_request(db) :
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
    test_user,
    sample_medical_institution_post_request,
):
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



