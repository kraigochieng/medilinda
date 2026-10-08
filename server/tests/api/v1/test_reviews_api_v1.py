import datetime
from types import SimpleNamespace

import pytest
from fastapi import status
from server.models.causality_assessment_level import (
    CausalityAssessmentLevelEnum,
    CausalityAssessmentLevelModel,
)
from server.models.review import ReviewModel
from server.repositories.adverse_drug_reaction_report import (
    AdverseDrugReactionReportRepository,
)

URL = "/api/v1/reviews/"
ME = "1"  # the signed-in user in the tests (see tests/dependencies.py)
OLD = datetime.datetime(2025, 1, 1, 9, 0, 0)
NEW = datetime.datetime(2025, 1, 2, 9, 0, 0)


# The test client closes the database session after every request, which detaches
# model objects. The fixtures therefore hold plain ids.
@pytest.fixture
def adr(db, sample_adverse_drug_reaction_report_post_request):
    model = AdverseDrugReactionReportRepository(db).create(
        data=sample_adverse_drug_reaction_report_post_request
    )
    return SimpleNamespace(id=model.id)


def add_assessment(db, adr, value=CausalityAssessmentLevelEnum.likely, created_at=OLD):
    cal = CausalityAssessmentLevelModel(
        adr_id=adr.id, causality_assessment_level_value=value, created_at=created_at
    )
    db.add(cal)
    db.commit()
    return SimpleNamespace(id=cal.id)


@pytest.fixture
def cal(db, adr):
    """The newest (and only) assessment, predicted 'likely'."""
    return add_assessment(db, adr)


def add_review(db, cal, user_id, approved=True):
    review = ReviewModel(
        causality_assessment_level_id=cal.id, user_id=user_id, approved=approved
    )
    db.add(review)
    db.commit()
    return SimpleNamespace(id=review.id)


def approve(cal, **overrides):
    return {"causality_assessment_level_id": cal.id, "approved": True, **overrides}


def reject(cal, **overrides):
    return {
        "causality_assessment_level_id": cal.id,
        "approved": False,
        "proposed_causality_level": "possible",
        "reason": "The dechallenge is unclear.",
        **overrides,
    }


class TestAddingAReview:
    def test_an_approval_is_saved_for_the_signed_in_user(self, client, cal):
        response = client.post(URL, json=approve(cal))

        assert response.status_code == status.HTTP_201_CREATED
        body = response.json()
        assert body["approved"] is True
        assert body["user_id"] == ME
        assert body["causality_assessment_level_id"] == cal.id

    def test_a_user_id_in_the_request_is_ignored(self, client, cal):
        response = client.post(URL, json=approve(cal, user_id="someone-else"))

        assert response.status_code == status.HTTP_201_CREATED
        assert response.json()["user_id"] == ME

    def test_a_rejection_keeps_the_proposed_level_and_reason(self, client, cal):
        response = client.post(URL, json=reject(cal))

        assert response.status_code == status.HTTP_201_CREATED
        body = response.json()
        assert body["approved"] is False
        assert body["proposed_causality_level"] == "possible"
        assert body["reason"] == "The dechallenge is unclear."

    def test_an_approval_does_not_keep_a_proposed_level(self, client, cal):
        response = client.post(
            URL, json=approve(cal, proposed_causality_level="certain", reason="Agreed")
        )

        assert response.status_code == status.HTTP_201_CREATED
        assert response.json()["proposed_causality_level"] is None
        assert response.json()["reason"] == "Agreed"

    def test_a_rejection_needs_a_proposed_level(self, client, cal):
        response = client.post(URL, json=reject(cal, proposed_causality_level=None))

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert "propose" in response.json()["error"]

    def test_the_proposed_level_must_differ_from_the_prediction(self, client, cal):
        response = client.post(URL, json=reject(cal, proposed_causality_level="likely"))

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert "differ" in response.json()["error"]

    @pytest.mark.parametrize("reason", [None, "", "  ", "ab"])
    def test_a_rejection_needs_a_reason(self, client, cal, reason):
        response = client.post(URL, json=reject(cal, reason=reason))

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert "reason" in response.json()["error"]

    def test_an_assessment_that_does_not_exist_is_a_404(self, client):
        response = client.post(
            URL, json={"causality_assessment_level_id": "nope", "approved": True}
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_an_assessment_replaced_by_an_edit_cannot_be_reviewed(self, client, db, adr, cal):
        add_assessment(db, adr, CausalityAssessmentLevelEnum.certain, created_at=NEW)

        response = client.post(URL, json=approve(cal))

        assert response.status_code == status.HTTP_409_CONFLICT
        assert "newer" in response.json()["error"]

    def test_the_newest_assessment_can_be_reviewed(self, client, db, adr, cal):
        newest = add_assessment(db, adr, CausalityAssessmentLevelEnum.certain, created_at=NEW)

        assert client.post(URL, json=approve(newest)).status_code == status.HTTP_201_CREATED

    def test_a_user_reviews_an_assessment_once(self, client, cal):
        assert client.post(URL, json=approve(cal)).status_code == status.HTTP_201_CREATED

        again = client.post(URL, json=reject(cal))

        assert again.status_code == status.HTTP_409_CONFLICT
        assert "already reviewed" in again.json()["error"]

    def test_another_user_can_review_the_same_assessment(self, client, db, cal):
        add_review(db, cal, "someone-else")

        assert client.post(URL, json=approve(cal)).status_code == status.HTTP_201_CREATED


class TestReading:
    def test_reviews_can_be_listed_and_filtered_by_user(self, client, db, cal):
        mine = add_review(db, cal, ME)
        add_review(db, cal, "someone-else")

        everyone = client.get(URL, params={"causality_assessment_level_id": cal.id}).json()
        only_mine = client.get(URL, params={"user_id": ME}).json()

        assert everyone["total"] == 2
        assert [r["id"] for r in only_mine["items"]] == [mine.id]

    def test_a_review_can_be_read_by_id(self, client, db, cal):
        review = add_review(db, cal, ME)

        response = client.get(f"{URL}{review.id}")

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["id"] == review.id


class TestChangingAReview:
    def test_the_author_can_change_their_review(self, client, db, cal):
        review = add_review(db, cal, ME, approved=True)

        response = client.put(f"{URL}{review.id}", json=reject(cal, reason="Changed my mind."))

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["approved"] is False
        assert response.json()["reason"] == "Changed my mind."

    def test_a_change_cannot_move_a_review_to_another_user_or_assessment(self, client, db, adr, cal):
        review = add_review(db, cal, ME)

        response = client.put(
            f"{URL}{review.id}",
            json={**approve(cal), "user_id": "someone-else", "causality_assessment_level_id": "other"},
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["user_id"] == ME
        assert response.json()["causality_assessment_level_id"] == cal.id

    def test_a_change_follows_the_same_rules_as_a_new_review(self, client, db, cal):
        review = add_review(db, cal, ME)

        response = client.put(f"{URL}{review.id}", json=reject(cal, proposed_causality_level=None))

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_nobody_else_can_change_it(self, client, db, cal):
        review = add_review(db, cal, "someone-else")

        response = client.put(f"{URL}{review.id}", json=approve(cal))

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert "own review" in response.json()["error"]

    def test_a_review_of_a_replaced_assessment_is_frozen(self, client, db, adr, cal):
        review = add_review(db, cal, ME)
        add_assessment(db, adr, CausalityAssessmentLevelEnum.certain, created_at=NEW)

        response = client.put(f"{URL}{review.id}", json=approve(cal))

        assert response.status_code == status.HTTP_409_CONFLICT

    def test_an_unknown_review_is_a_404(self, client, cal):
        assert client.put(f"{URL}nope", json=approve(cal)).status_code == status.HTTP_404_NOT_FOUND


class TestDeletingAReview:
    def test_the_author_can_delete_their_review(self, client, db, cal):
        review = add_review(db, cal, ME)

        assert client.delete(f"{URL}{review.id}").status_code == status.HTTP_204_NO_CONTENT
        assert client.get(f"{URL}{review.id}").status_code == status.HTTP_404_NOT_FOUND

    def test_nobody_else_can_delete_it(self, client, db, cal):
        review = add_review(db, cal, "someone-else")

        assert client.delete(f"{URL}{review.id}").status_code == status.HTTP_403_FORBIDDEN
        assert client.get(f"{URL}{review.id}").status_code == status.HTTP_200_OK

    def test_a_review_of_a_replaced_assessment_cannot_be_deleted(self, client, db, adr, cal):
        review = add_review(db, cal, ME)
        add_assessment(db, adr, CausalityAssessmentLevelEnum.certain, created_at=NEW)

        assert client.delete(f"{URL}{review.id}").status_code == status.HTTP_409_CONFLICT
