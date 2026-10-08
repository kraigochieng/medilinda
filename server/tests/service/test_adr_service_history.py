from unittest.mock import Mock

import pytest
from server.basemodels.causality_asssessment_level import (
    CausalityAssessmentLevelPostRequest,
)
from server.basemodels.sms import SMSMessageTypeEnum
from server.exceptions import ResourceConflictError, ResourceNotFoundError
from server.models.adverse_drug_reaction_report import ADRModel
from server.models.audit_log import AuditLogModel
from server.models.causality_assessment_level import (
    CausalityAssessmentLevelEnum,
    CausalityAssessmentLevelModel,
)
from server.models.review import ReviewModel
from server.models.sms import SMSMessageModel
from server.services.adverse_drug_reaction_report import (
    AdverseDrugReactionReportService,
)
from server.utils.audit import Actor, bind_actor, serialize_row

ALICE = Actor(id="user-alice", username="alice")
Level = CausalityAssessmentLevelEnum


@pytest.fixture
def service(db, mocker):
    """A service whose ML prediction is replaced by a fixed sequence of levels."""
    svc = AdverseDrugReactionReportService(
        db=db, ml_model=Mock(), encoder=Mock(), explainer=Mock()
    )
    levels = iter([Level.likely, Level.certain, Level.possible, Level.unlikely])

    def fake_generate(adr_model):
        return CausalityAssessmentLevelPostRequest(
            adr_id=adr_model.id, causality_assessment_level_value=next(levels)
        )

    mocker.patch.object(
        svc, "_generate_causality_assessment_data", side_effect=fake_generate
    )
    return svc


@pytest.fixture
def adr_data(sample_adverse_drug_reaction_report_post_request):
    return sample_adverse_drug_reaction_report_post_request


def assessments(db, adr_id):
    return (
        db.query(CausalityAssessmentLevelModel)
        .filter_by(adr_id=adr_id)
        .order_by(CausalityAssessmentLevelModel.created_at)
        .all()
    )


def audit(db, **filters):
    return (
        db.query(AuditLogModel)
        .filter_by(**filters)
        .order_by(AuditLogModel.at, AuditLogModel.seq)
        .all()
    )


class TestCreate:
    def test_saves_the_adr_and_its_first_assessment_in_one_audit_group(
        self, db, service, adr_data
    ):
        group_id = bind_actor(ALICE)

        created = service.create_and_predict(adr_data)

        (cal,) = assessments(db, created.id)
        assert cal.causality_assessment_level_value == Level.likely
        rows = audit(db)
        assert {(r.entity_type, r.action) for r in rows} == {
            ("adr", "create"),
            ("causality_assessment_level", "create"),
        }
        assert {r.group_id for r in rows} == {group_id}
        assert {r.root_id for r in rows} == {created.id}

    def test_nothing_is_saved_if_the_prediction_fails(self, db, service, adr_data):
        service._generate_causality_assessment_data.side_effect = RuntimeError("model down")
        bind_actor(ALICE)

        with pytest.raises(RuntimeError):
            service.create_and_predict(adr_data)

        assert db.query(ADRModel).count() == 0
        assert db.query(AuditLogModel).count() == 0


class TestUpdate:
    @pytest.fixture
    def created(self, db, service, adr_data):
        bind_actor(ALICE)
        return service.create_and_predict(adr_data)

    def test_a_change_to_a_model_input_adds_a_new_assessment(
        self, db, service, adr_data, created, test_user
    ):
        (first,) = assessments(db, created.id)
        db.add(
            ReviewModel(
                causality_assessment_level_id=first.id,
                user_id=test_user.id,
                approved=True,
            )
        )
        db.commit()

        service.update_and_predict(
            created.id, adr_data.model_copy(update={"rifampicin_suspected": False})
        )

        old, new = assessments(db, created.id)
        assert old.id == first.id
        assert old.causality_assessment_level_value == Level.likely
        assert new.causality_assessment_level_value == Level.certain
        # The review stays with the prediction it judged; the new one has none.
        assert db.query(ReviewModel).filter_by(causality_assessment_level_id=old.id).count() == 1
        assert db.query(ReviewModel).filter_by(causality_assessment_level_id=new.id).count() == 0

    def test_the_edit_is_in_the_audit_log_with_old_and_new_values(
        self, db, service, adr_data, created
    ):
        service.update_and_predict(
            created.id, adr_data.model_copy(update={"patient_name": "Renamed"})
        )

        update = audit(db, entity_type="adr", action="update")[0]
        assert update.version == 2
        assert update.actor_username == "alice"
        assert {"field": "patient_name", "old": "Jane Smith", "new": "Renamed"} in update.changes
        assert update.snapshot["patient_name"] == "Renamed"
        assert len(assessments(db, created.id)) == 2  # patient_name feeds the model

    def test_a_change_to_a_field_the_model_ignores_keeps_the_assessment(
        self, db, service, adr_data, created
    ):
        service.update_and_predict(
            created.id, adr_data.model_copy(update={"comments": "Follow-up done."})
        )

        assert len(assessments(db, created.id)) == 1
        assert audit(db, entity_type="adr", action="update")[0].changes == [
            {
                "field": "comments",
                "old": adr_data.comments,
                "new": "Follow-up done.",
            }
        ]

    def test_saving_without_changes_does_nothing(self, db, service, adr_data, created):
        service.update_and_predict(created.id, adr_data)

        assert len(assessments(db, created.id)) == 1
        assert audit(db, entity_type="adr", action="update") == []

    def test_the_creator_of_a_report_never_changes(
        self, db, service, adr_data, created, test_user
    ):
        service.update_and_predict(
            created.id,
            adr_data.model_copy(update={"user_id": "someone-else", "comments": "x"}),
        )

        assert db.get(ADRModel, created.id).user_id == test_user.id

    def test_nothing_is_saved_if_the_new_prediction_fails(
        self, db, service, adr_data, created
    ):
        service._generate_causality_assessment_data.side_effect = RuntimeError("model down")

        with pytest.raises(RuntimeError):
            service.update_and_predict(
                created.id, adr_data.model_copy(update={"rifampicin_suspected": False})
            )

        db.expire_all()
        assert db.get(ADRModel, created.id).rifampicin_suspected is True
        assert len(assessments(db, created.id)) == 1
        assert audit(db, entity_type="adr", action="update") == []

    def test_unknown_adr_is_a_404(self, service, adr_data):
        with pytest.raises(ResourceNotFoundError):
            service.update_and_predict("missing", adr_data)


class TestDeleteAndRestore:
    @pytest.fixture
    def adr_with_history(self, db, service, adr_data, test_user):
        bind_actor(ALICE)
        created = service.create_and_predict(adr_data)
        (cal,) = assessments(db, created.id)
        db.add(
            ReviewModel(
                causality_assessment_level_id=cal.id,
                user_id=test_user.id,
                approved=True,
                reason="Looks right",
            )
        )
        db.add(
            SMSMessageModel(
                adr_id=created.id,
                sms_type=list(SMSMessageTypeEnum)[0],
                number="+254700000000",
                content="Alert",
                cost="KES 1",
                status="Sent",
                status_code=101,
            )
        )
        db.commit()
        return created.id

    def snapshots(self, db, adr_id):
        return {
            "adr": serialize_row(db.get(ADRModel, adr_id)),
            "cals": [serialize_row(c) for c in assessments(db, adr_id)],
            "reviews": [serialize_row(r) for r in db.query(ReviewModel).all()],
        }

    def test_delete_removes_the_adr_assessments_and_reviews(
        self, db, service, adr_with_history
    ):
        service.delete_by_id(adr_with_history)

        assert db.query(ADRModel).count() == 0
        assert db.query(CausalityAssessmentLevelModel).count() == 0
        assert db.query(ReviewModel).count() == 0

    def test_delete_keeps_the_sms_log_but_unlinks_it(self, db, service, adr_with_history):
        service.delete_by_id(adr_with_history)

        (sms,) = db.query(SMSMessageModel).all()
        assert sms.adr_id is None

    def test_delete_is_one_audit_group_with_a_snapshot_of_everything(
        self, db, service, adr_with_history
    ):
        service.delete_by_id(adr_with_history)

        deletes = audit(db, action="delete")
        assert {r.entity_type for r in deletes} == {
            "adr",
            "causality_assessment_level",
            "review",
        }
        assert len({r.group_id for r in deletes}) == 1
        sms_update = audit(db, entity_type="sms_message", action="update")[-1]
        assert sms_update.group_id == deletes[0].group_id
        assert {"field": "adr_id", "old": adr_with_history, "new": None} in sms_update.changes

    def test_restore_brings_back_exactly_what_was_deleted(
        self, db, service, adr_with_history
    ):
        before = self.snapshots(db, adr_with_history)
        service.delete_by_id(adr_with_history)

        restored = service.restore(adr_with_history)

        assert restored.id == adr_with_history
        assert self.snapshots(db, adr_with_history) == before
        (sms,) = db.query(SMSMessageModel).all()
        assert sms.adr_id == adr_with_history  # relinked
        restored_rows = audit(db, action="restore")
        assert {r.entity_type for r in restored_rows} == {
            "adr",
            "causality_assessment_level",
            "review",
        }

    def test_the_history_continues_after_a_restore(self, db, service, adr_with_history):
        service.delete_by_id(adr_with_history)
        service.restore(adr_with_history)

        versions = [
            (r.version, r.action)
            for r in audit(db, entity_type="adr", entity_id=adr_with_history)
        ]
        assert versions == [(1, "create"), (2, "delete"), (3, "restore")]

    def test_restore_undoes_only_the_delete_not_earlier_edits_in_the_same_request(
        self, db, service, adr_data, adr_with_history
    ):
        """Everything here runs under one bound actor, so it is one audit group."""
        service.update_and_predict(
            adr_with_history, adr_data.model_copy(update={"comments": "Edited"})
        )
        service.delete_by_id(adr_with_history)

        service.restore(adr_with_history)

        assert db.get(ADRModel, adr_with_history).comments == "Edited"
        actions = [
            r.action for r in audit(db, entity_type="adr", entity_id=adr_with_history)
        ]
        assert actions == ["create", "update", "delete", "restore"]  # no extra update

    def test_restoring_something_that_was_never_deleted_is_a_404(self, service):
        with pytest.raises(ResourceNotFoundError):
            service.restore("never-existed")

    def test_restoring_twice_is_a_conflict(self, service, adr_with_history):
        service.delete_by_id(adr_with_history)
        service.restore(adr_with_history)

        with pytest.raises(ResourceConflictError):
            service.restore(adr_with_history)
