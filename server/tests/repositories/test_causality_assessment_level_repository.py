import pytest
from server.basemodels.causality_asssessment_level import (
    CausalityAssessmentLevelEnum,
    CausalityAssessmentLevelPostRequest,
)
from server.models.causality_assessment_level import CausalityAssessmentLevelModel
from server.repositories.causality_assessment_level import (
    CausalityAssessmentLevelRepository,
)


@pytest.fixture
def cal_repository(db):
    """Fixture for the CausalityAssessmentLevel repository."""
    return CausalityAssessmentLevelRepository(db)


@pytest.fixture
def sample_cal_request():
    """Fixture for creating a base Causality Assessment Level."""
    return CausalityAssessmentLevelPostRequest(
        adr_id="adr-123",
        ml_model_id="model-123",
        causality_assessment_level_value=CausalityAssessmentLevelEnum.possible,
        base_values=None,
        shap_values_matrix=None,
        shap_values_sum_per_class=None,
        shap_values_and_base_values_sum_per_class=None,
        feature_names=None,
        feature_values=None,
    )


@pytest.fixture
def sample_cal_request_updated():
    """Fixture for updating an existing Causality Assessment Level."""
    return CausalityAssessmentLevelPostRequest(
        adr_id="adr-123",
        ml_model_id="model-123",
        causality_assessment_level_value=CausalityAssessmentLevelEnum.likely,
        base_values=None,
        shap_values_matrix=None,
        shap_values_sum_per_class=None,
        shap_values_and_base_values_sum_per_class=None,
        feature_names=None,
        feature_values=None,
    )


def test_create_and_get_by_id(cal_repository, db, sample_cal_request):
    """Test manually creating and fetching a CausalityAssessmentLevelModel."""
    cal_model = CausalityAssessmentLevelModel(**sample_cal_request.model_dump())
    db.add(cal_model)
    db.commit()
    db.refresh(cal_model)

    fetched = cal_repository.get_by_id(cal_model.id)

    assert fetched is not None
    assert fetched.id == cal_model.id
    assert fetched.adr_id == "adr-123"
    assert fetched.ml_model_id == "model-123"
    assert (
        fetched.causality_assessment_level_value == CausalityAssessmentLevelEnum.possible
    )


def test_get_all(cal_repository, db, sample_cal_request):
    """Test pagination and multiple records retrieval."""
    for i in range(3):
        model = CausalityAssessmentLevelModel(
            adr_id=f"adr-{i}",
            ml_model_id=f"model-{i}",
            causality_assessment_level_value=CausalityAssessmentLevelEnum.possible,
            base_values=None,
            shap_values_matrix=None,
            shap_values_sum_per_class=None,
            shap_values_and_base_values_sum_per_class=None,
            feature_names=None,
            feature_values=None,
        )
        db.add(model)
    db.commit()

    page = cal_repository.get_all()

    assert page is not None
    assert len(page.items) == 3
    assert page.total == 3


def test_update_existing_level(
    cal_repository, db, sample_cal_request, sample_cal_request_updated
):
    """Test that an existing record can be updated."""
    cal_model = CausalityAssessmentLevelModel(**sample_cal_request.model_dump())
    db.add(cal_model)
    db.commit()
    db.refresh(cal_model)

    updated = cal_repository.update(cal_model.id, sample_cal_request_updated)

    assert updated is not None
    assert (
        updated.causality_assessment_level_value == CausalityAssessmentLevelEnum.likely
    )
    assert updated.adr_id == "adr-123"
    assert updated.ml_model_id == "model-123"


def test_update_nonexistent_level(cal_repository, sample_cal_request_updated):
    """Test updating a non-existing record returns None."""
    result = cal_repository.update("non-existent-id", sample_cal_request_updated)
    assert result is None


def test_delete_existing_level(cal_repository, db, sample_cal_request):
    """Test deleting an existing record."""
    cal_model = CausalityAssessmentLevelModel(**sample_cal_request.model_dump())
    db.add(cal_model)
    db.commit()
    db.refresh(cal_model)

    deleted = cal_repository.delete(cal_model.id)
    assert deleted is True
    assert cal_repository.get_by_id(cal_model.id) is None


def test_delete_nonexistent_level(cal_repository):
    """Test deleting a non-existing record returns False."""
    result = cal_repository.delete("non-existent-id")
    assert result is False
