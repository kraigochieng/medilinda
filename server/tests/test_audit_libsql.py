"""Production stores app data in Turso through the libsql driver. Run the audit
lifecycle through that same driver (on a local file) so a driver difference in
batch inserts or row-value queries shows up here, not in production."""

from unittest.mock import Mock

import pytest
from server.basemodels.causality_asssessment_level import (
    CausalityAssessmentLevelPostRequest,
)
from server.db.base import Base
from server.models.adverse_drug_reaction_report import ADRModel
from server.models.audit_log import AuditLogModel
from server.models.causality_assessment_level import CausalityAssessmentLevelEnum
from server.models.medical_institution import MedicalInstitutionModel
from server.models.user import UserModel
from server.services.adverse_drug_reaction_report import (
    AdverseDrugReactionReportService,
)
from server.utils.audit import Actor, bind_actor
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

pytest.importorskip("sqlalchemy_libsql")


@pytest.fixture
def libsql_db(tmp_path):
    engine = create_engine(f"sqlite+libsql:///{tmp_path / 'app.db'}")
    Base.metadata.create_all(engine)
    session = sessionmaker(bind=engine)()
    try:
        yield session
    finally:
        session.close()
        engine.dispose()


def test_lifecycle_through_the_libsql_driver(
    libsql_db, sample_adverse_drug_reaction_report_post_request, mocker
):
    db = libsql_db
    data = sample_adverse_drug_reaction_report_post_request
    db.add(UserModel(id=data.user_id, username="u", password="x"))
    db.add(MedicalInstitutionModel(id=data.medical_institution_id, name="H", mfl_code="1"))
    db.commit()

    service = AdverseDrugReactionReportService(
        db=db, ml_model=Mock(), encoder=Mock(), explainer=Mock()
    )
    mocker.patch.object(
        service,
        "_generate_causality_assessment_data",
        side_effect=lambda adr_model: CausalityAssessmentLevelPostRequest(
            adr_id=adr_model.id,
            causality_assessment_level_value=CausalityAssessmentLevelEnum.likely,
        ),
    )
    bind_actor(Actor(id="a", username="alice"))

    created = service.create_and_predict(data)
    service.update_and_predict(
        created.id, data.model_copy(update={"rifampicin_suspected": False})
    )
    service.delete_by_id(created.id)
    restored = service.restore(created.id)

    assert restored.id == created.id
    rows = (
        db.query(AuditLogModel)
        .filter_by(entity_type="adr", entity_id=created.id)
        .order_by(AuditLogModel.version)
        .all()
    )
    assert [(r.version, r.action) for r in rows] == [
        (1, "create"),
        (2, "update"),
        (3, "delete"),
        (4, "restore"),
    ]
    assert rows[1].changes[0]["field"] == "rifampicin_suspected"
    assert rows[3].snapshot["patient_name"] == data.patient_name
    # The earlier edit is still in place: restore undid only the delete.
    assert db.get(ADRModel, created.id).rifampicin_suspected is False
