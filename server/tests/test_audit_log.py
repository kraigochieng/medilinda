import pytest
from server.models.audit_log import AuditLogModel
from server.models.adverse_drug_reaction_report import ADRModel
from server.models.causality_assessment_level import (
    CausalityAssessmentLevelEnum,
    CausalityAssessmentLevelModel,
)
from server.models.review import ReviewModel
from server.models.user import UserModel
from server.repositories.adverse_drug_reaction_report import (
    AdverseDrugReactionReportRepository,
)
from server.utils.audit import (
    Actor,
    audit_action,
    bind_actor,
    deserialize_row,
    serialize_row,
)

ALICE = Actor(id="user-alice", username="alice")


def log_rows(db, **filters):
    query = db.query(AuditLogModel).filter_by(**filters)
    return query.order_by(AuditLogModel.entity_id, AuditLogModel.version, AuditLogModel.seq).all()


@pytest.fixture
def adr_data(sample_adverse_drug_reaction_report_post_request):
    return sample_adverse_drug_reaction_report_post_request


def create_adr(db, data):
    return AdverseDrugReactionReportRepository(db).create(data=data)


def add_assessment_and_review(db, adr, user):
    cal = CausalityAssessmentLevelModel(
        adr_id=adr.id,
        causality_assessment_level_value=CausalityAssessmentLevelEnum.likely,
    )
    db.add(cal)
    db.commit()
    review = ReviewModel(
        causality_assessment_level_id=cal.id, user_id=user.id, approved=True
    )
    db.add(review)
    db.commit()
    return cal, review


class TestRecording:
    def test_nothing_is_recorded_without_an_actor(self, db, adr_data):
        create_adr(db, adr_data)

        assert db.query(AuditLogModel).count() == 0

    def test_create_is_recorded_with_who_when_and_a_snapshot(self, db, adr_data):
        group_id = bind_actor(ALICE)

        adr = create_adr(db, adr_data)

        (row,) = log_rows(db, entity_type="adr")
        assert row.entity_id == adr.id
        assert (row.action, row.version) == ("create", 1)
        assert (row.actor_id, row.actor_username) == ("user-alice", "alice")
        assert row.at is not None
        assert row.group_id == group_id
        assert (row.root_type, row.root_id) == ("adr", adr.id)
        assert row.snapshot["patient_name"] == adr_data.patient_name
        assert row.snapshot["patient_gender"] == "female"  # enums are stored by value
        assert row.changes is None

    def test_update_records_old_and_new_values(self, db, adr_data):
        bind_actor(ALICE)
        adr = create_adr(db, adr_data)

        adr.patient_name = "Changed Name"
        adr.patient_age = 50
        db.commit()

        rows = log_rows(db, entity_type="adr")
        assert [r.version for r in rows] == [1, 2]
        update = rows[1]
        assert update.action == "update"
        by_field = {c["field"]: c for c in update.changes}
        assert by_field["patient_name"] == {
            "field": "patient_name",
            "old": "Jane Smith",
            "new": "Changed Name",
        }
        assert by_field["patient_age"]["old"] == 45
        assert by_field["patient_age"]["new"] == 50
        assert "updated_at" not in by_field
        assert update.snapshot["patient_name"] == "Changed Name"

    def test_an_update_that_changes_nothing_is_not_recorded(self, db, adr_data):
        bind_actor(ALICE)
        adr = create_adr(db, adr_data)

        adr.patient_name = adr.patient_name  # same value
        db.commit()

        assert len(log_rows(db, entity_type="adr")) == 1

    def test_versions_keep_counting_up(self, db, adr_data):
        bind_actor(ALICE)
        adr = create_adr(db, adr_data)

        for name in ["A", "B", "C"]:
            adr.patient_name = name
            db.commit()

        assert [r.version for r in log_rows(db, entity_type="adr")] == [1, 2, 3, 4]

    def test_an_old_row_gets_a_baseline_version_before_its_first_change(
        self, db, adr_data
    ):
        adr = create_adr(db, adr_data)  # no actor: exists before auditing
        assert db.query(AuditLogModel).count() == 0

        bind_actor(ALICE)
        adr.patient_name = "Changed Name"
        db.commit()

        baseline, update = log_rows(db, entity_type="adr")
        assert (baseline.version, baseline.action) == (1, "create")
        assert baseline.actor_username == "system (baseline)"
        assert baseline.snapshot["patient_name"] == "Jane Smith"  # the old value
        assert (update.version, update.action) == (2, "update")
        assert update.actor_username == "alice"

    def test_restore_label_is_used_for_creates_in_the_block(self, db, adr_data):
        bind_actor(ALICE)
        with audit_action("restore"):
            create_adr(db, adr_data)

        (row,) = log_rows(db, entity_type="adr")
        assert row.action == "restore"


class TestDelete:
    def test_delete_records_the_whole_cascade_in_one_group(
        self, db, adr_data, test_user
    ):
        adr = create_adr(db, adr_data)
        cal, review = add_assessment_and_review(db, adr, test_user)
        group_id = bind_actor(ALICE)

        db.delete(adr)
        db.commit()

        deletes = [r for r in log_rows(db) if r.action == "delete"]
        assert {r.entity_type for r in deletes} == {
            "adr",
            "causality_assessment_level",
            "review",
        }
        assert {r.group_id for r in deletes} == {group_id}
        # Children are removed first, so they are logged first.
        order = [r.entity_type for r in sorted(deletes, key=lambda r: r.seq)]
        assert order.index("review") < order.index("causality_assessment_level")
        assert order.index("causality_assessment_level") < order.index("adr")
        assert {r.root_id for r in deletes} == {adr.id}

        adr_delete = next(r for r in deletes if r.entity_type == "adr")
        assert adr_delete.snapshot["patient_name"] == "Jane Smith"
        review_delete = next(r for r in deletes if r.entity_type == "review")
        assert review_delete.snapshot["approved"] is True
        assert review_delete.snapshot["causality_assessment_level_id"] == cal.id

    def test_a_review_is_linked_to_its_adr_through_the_assessment(
        self, db, adr_data, test_user
    ):
        adr = create_adr(db, adr_data)
        cal, _ = add_assessment_and_review(db, adr, test_user)
        bind_actor(ALICE)

        review = ReviewModel(
            causality_assessment_level_id=cal.id, user_id=test_user.id, approved=False
        )
        db.add(review)
        db.commit()

        (row,) = log_rows(db, entity_type="review", entity_id=review.id)
        assert (row.root_type, row.root_id) == ("adr", adr.id)


class TestSnapshots:
    def test_secrets_are_never_serialised(self, test_user):
        snapshot = serialize_row(test_user)

        assert "password" not in snapshot
        assert snapshot["username"] == test_user.username

    def test_a_snapshot_rebuilds_the_same_row(self, db, adr_data):
        adr = create_adr(db, adr_data)
        snapshot = serialize_row(adr)

        rebuilt = ADRModel(**deserialize_row(ADRModel, snapshot))

        assert serialize_row(rebuilt) == snapshot
        assert rebuilt.patient_gender == adr.patient_gender  # an enum, not a string
        assert rebuilt.patient_date_of_birth == adr.patient_date_of_birth  # a date

    def test_unaudited_tables_are_ignored(self, db):
        bind_actor(ALICE)
        db.add(UserModel(id="u1", username="u1", password="x"))
        db.commit()

        assert db.query(AuditLogModel).count() == 0
