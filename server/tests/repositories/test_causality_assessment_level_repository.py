import pytest
from fastapi_pagination import Params
from server.basemodels.causality_asssessment_level import (
    CausalityAssessmentLevelEnum,
    CausalityAssessmentLevelPostRequest,
)
from server.exceptions import ResourceNotFoundError
from server.models.causality_assessment_level import CausalityAssessmentLevelModel
from server.repositories.causality_assessment_level import (
    CausalityAssessmentLevelRepository,
)


@pytest.fixture
def cal_repository(db):
    """Fixture for the CausalityAssessmentLevel repository."""
    return CausalityAssessmentLevelRepository(db)


@pytest.fixture
def sample_causality_assessment_level_post_request():
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
def sample_causality_assessment_level_post_request_updated():
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


def test_get_all(cal_repository, sample_causality_assessment_level_post_request):
    """Test pagination and multiple records retrieval."""
    for i in range(3):
        cal_repository.create(sample_causality_assessment_level_post_request)

    page = cal_repository.get_all(
        pagination_params=Params(page=1, size=50), adr_id=None
    )

    assert page is not None
    assert len(page.items) == 3
    assert page.total == 3


def test_update_existing_level(
    cal_repository,
    db,
    sample_causality_assessment_level_post_request,
    sample_causality_assessment_level_post_request_updated,
):
    """Test that an existing record can be updated."""
    cal_model = CausalityAssessmentLevelModel(
        **sample_causality_assessment_level_post_request.model_dump()
    )
    db.add(cal_model)
    db.commit()
    db.refresh(cal_model)

    created = cal_repository.create(data=sample_causality_assessment_level_post_request)

    updated = cal_repository.update(
        cal_model.id, sample_causality_assessment_level_post_request_updated
    )

    assert updated is not None
    assert (
        updated.causality_assessment_level_value == CausalityAssessmentLevelEnum.likely
    )
    assert updated.adr_id == "adr-123"
    assert updated.ml_model_id == "model-123"


def test_update_nonexistent_level(
    cal_repository, sample_causality_assessment_level_post_request_updated
):
    """Test updating a non-existing record returns None."""
    with pytest.raises(ResourceNotFoundError):
        cal_repository.update(
            id="non-existent-id",
            data=sample_causality_assessment_level_post_request_updated,
        )


def test_delete_existing_level(
    cal_repository, db, sample_causality_assessment_level_post_request
):
    """Test deleting an existing record."""
    cal_model = CausalityAssessmentLevelModel(
        **sample_causality_assessment_level_post_request.model_dump()
    )

    db.add(cal_model)
    db.commit()
    db.refresh(cal_model)

    cal_repository.delete(cal_model.id)

    with pytest.raises(ResourceNotFoundError):
        cal_repository.get_by_id(cal_model.id)


def test_delete_nonexistent_level(cal_repository):
    """Test deleting a non-existing record returns False."""
    with pytest.raises(ResourceNotFoundError):
        cal_repository.delete(id="non-existent-id")
