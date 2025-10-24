from fastapi import status
from server.basemodels.review import ADRReviewCreateRequest
from server.models.causality_assessment_level import CausalityAssessmentLevelModel
from server.models.review import ReviewModel
from server.models.user import UserModel

path = "/api/v1/reviews"


def test_create_review(client, db):
    review_data = ADRReviewCreateRequest(
        approved=True, proposed_causality_level=None, reason="Initial approval"
    )
    # You need to create a valid causality_assessment_level_id and user_id for a real test
    review = ReviewModel(
        causality_assessment_level_id="test_causality_id",
        user_id="test_user_id",
        approved=review_data.approved,
        proposed_causality_level=review_data.proposed_causality_level,
        reason=review_data.reason,
    )
    db.add(review)
    db.commit()
    db.refresh(review)
    assert review.id is not None

    def test_get_reviews(client, db):
        # Create a user
        user = UserModel(
            id="test_user_id", name="Test User", email="testuser@example.com"
        )
        db.add(user)
        # Create a causality assessment level
        cal = CausalityAssessmentLevelModel(id="test_causality_id", name="Test Level")
        db.add(cal)
        db.commit()

        db.add(
            ReviewModel(
                causality_assessment_level_id=cal.id,
                user_id=user.id,
                approved=True,
                reason="Test reason",
            )
        )
        db.commit()
        response = client.get(path)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "items" in data
        assert any("Test reason" in r["reason"] for r in data["items"])


def test_get_review_by_id(client, db):
    review = ReviewModel(
        causality_assessment_level_id="test_causality_id",
        user_id="test_user_id",
        approved=True,
        reason="Find me",
    )
    db.add(review)
    db.commit()
    db.refresh(review)
    response = client.get(f"{path}/{review.id}")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["reason"] == "Find me"


def test_get_review_by_id_not_found(client):
    response = client.get(f"{path}/doesnotexist")
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_update_review_by_id(client, db):
    review = ReviewModel(
        causality_assessment_level_id="test_causality_id",
        user_id="test_user_id",
        approved=False,
        reason="Old reason",
    )
    db.add(review)
    db.commit()
    db.refresh(review)
    payload = {
        "approved": True,
        "proposed_causality_level": None,
        "reason": "Updated reason",
    }
    response = client.put(f"{path}/{review.id}", json=payload)
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["reason"] == "Updated reason"
    assert response.json()["approved"] is True


def test_update_review_by_id_not_found(client):
    payload = {
        "approved": True,
        "proposed_causality_level": None,
        "reason": "No review",
    }
    response = client.put(f"{path}/doesnotexist", json=payload)
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_delete_review_by_id(client, db):
    review = ReviewModel(
        causality_assessment_level_id="test_causality_id",
        user_id="test_user_id",
        approved=True,
        reason="Delete me",
    )
    db.add(review)
    db.commit()
    db.refresh(review)
    response = client.delete(f"{path}/{review.id}")
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert db.query(ReviewModel).filter_by(id=review.id).first() is None


def test_delete_review_by_id_not_found(client):
    response = client.delete(f"{path}/doesnotexist")
    assert response.status_code == status.HTTP_404_NOT_FOUND
