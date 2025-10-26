import pytest
from server.basemodels.causality_asssessment_level import CausalityAssessmentLevelEnum
from server.basemodels.review import ReviewPostRequest
from server.repositories.review import ReviewRepository


@pytest.fixture
def review_repository(db):
    return ReviewRepository(db)


@pytest.fixture
def sample_review_request():
    return ReviewPostRequest(
        causality_assessment_level_id="1",
        user_id="1",
        proposed_causality_level=CausalityAssessmentLevelEnum.possible,
        reason="my reason",
        approved=True,
    )


@pytest.fixture
def sample_review_request_updated():
    return ReviewPostRequest(
        causality_assessment_level_id="1",
        user_id="1",
        proposed_causality_level=CausalityAssessmentLevelEnum.possible,
        reason="another reason",
        approved=True,
    )


def test_create_review(review_repository, sample_review_request):
    review = review_repository.create(sample_review_request)

    assert review.id is not None


def test_get_review(review_repository, sample_review_request):
    created = review_repository.create(sample_review_request)
    fetched = review_repository.get(created.id)

    assert fetched.id == created.id


def test_update_review(
    review_repository, sample_review_request, sample_review_request_updated
):
    created = review_repository.create(sample_review_request)
    updated = review_repository.update(created.id, sample_review_request_updated)
    
    assert updated.reason == "another reason"


def test_delete_review(review_repository, sample_review_request):
    created = review_repository.create(sample_review_request)
    deleted = review_repository.delete(created.id)

    assert deleted is True
    assert review_repository.get(created.id) is None


def test_get_all_and_pagination(review_repository, sample_review_request):
    for i in range(3):
        review_repository.create(
            ReviewPostRequest(
                causality_assessment_level_id=f"{i} + 1",
                user_id="1",
                proposed_causality_level=CausalityAssessmentLevelEnum.possible,
                reason=f"reason {i}",
                approved=True,
            )
        )

    page = review_repository.get_all(causality_assessment_level_id=None)

    assert len(page.items) == 3
    assert page.total == 3
