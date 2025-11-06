import pytest
from server.basemodels.causality_asssessment_level import CausalityAssessmentLevelEnum
from server.basemodels.review import ReviewPostRequest
from server.exceptions import ResourceNotFoundError
from server.repositories.review import ReviewRepository
from fastapi_pagination import Params


@pytest.fixture
def review_repository(db):
    return ReviewRepository(db=db)


@pytest.fixture
def sample_review_request() -> ReviewPostRequest:
    return ReviewPostRequest(
        causality_assessment_level_id="1",
        user_id="1",
        proposed_causality_level=CausalityAssessmentLevelEnum.possible,
        reason="my reason",
        approved=True,
    )


@pytest.fixture
def sample_review_request_updated(sample_review_request) -> ReviewPostRequest:
    updated = sample_review_request.model_copy()

    updated.reason = "another reason"

    return updated


def test_create_review(review_repository, sample_review_request):
    review = review_repository.create(data=sample_review_request)

    assert review.id is not None


def test_get_review(review_repository, sample_review_request):
    created = review_repository.create(data=sample_review_request)
    fetched = review_repository.get(id=created.id)

    assert fetched.id == created.id


def test_update_review(
    review_repository, sample_review_request, sample_review_request_updated
):
    created = review_repository.create(data=sample_review_request)
    updated = review_repository.update(
        id=created.id, data=sample_review_request_updated
    )

    assert updated.reason == sample_review_request_updated.reason


def test_delete_review(review_repository, sample_review_request):
    created = review_repository.create(sample_review_request)

    review_repository.delete(created.id)

    with pytest.raises(ResourceNotFoundError):
        review_repository.get(id=created.id)


def test_get_all_and_pagination(review_repository, sample_review_request):
    for i in range(3):
        review_repository.create(sample_review_request)

    page = review_repository.get_all(
        causality_assessment_level_id=None,
        user_id=None,
        pagination_params=Params(page=1, size=50),
    )

    assert len(page.items) == 3
    assert page.total == 3
