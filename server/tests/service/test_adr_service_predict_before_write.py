"""The ADR service must run the model before it writes (issue #110).

On Turso the stream of a connection closes after a short idle time. If the model
runs while the session holds an open transaction, the later commit can fail.
"""

from unittest.mock import Mock

import numpy as np
import pandas as pd
import pytest
from shap import Explanation
from server.basemodels.adverse_drug_reaction_report import ADRPostRequest, MLModelInput
from server.models.adverse_drug_reaction_report import ADRModel
from server.models.causality_assessment_level import CausalityAssessmentLevelModel
from server.services.adverse_drug_reaction_report import (
    AdverseDrugReactionReportService,
)
from sqlalchemy.orm import Session


class FakeMlModel:
    """A model that records its input and whether the session was in a transaction."""

    def __init__(self, *, db: Session, error: Exception | None = None) -> None:
        self.db: Session = db
        self.error: Exception | None = error
        self.inputs: list[pd.DataFrame] = []
        self.in_transaction_during_predict: list[bool] = []

    def predict(self, frame: pd.DataFrame) -> np.ndarray:
        self.inputs.append(frame.copy())
        self.in_transaction_during_predict.append(self.db.in_transaction())
        if self.error is not None:
            raise self.error
        return np.array([0])


def build_service(
    *, db: Session, ml_model: FakeMlModel
) -> AdverseDrugReactionReportService:
    encoder = Mock()
    encoder.inverse_transform.return_value = np.array([["likely"]])
    explanation = Explanation(
        values=np.zeros((1, 1, 3)),
        base_values=np.zeros((1, 3)),
        data=np.array([[1.0]]),
        feature_names=["f1"],
    )
    explainer = Mock(return_value=explanation)
    return AdverseDrugReactionReportService(
        db=db, ml_model=ml_model, encoder=encoder, explainer=explainer
    )


def expected_frame(adr_model: ADRModel) -> pd.DataFrame:
    """The model input that the service must build for a saved ADR."""
    frame = pd.DataFrame([MLModelInput.model_validate(adr_model).model_dump()])
    frame["created_at"] = frame["created_at"].astype(str)
    return frame


@pytest.fixture
def adr_data(sample_adverse_drug_reaction_report_post_request) -> ADRPostRequest:
    return sample_adverse_drug_reaction_report_post_request


@pytest.fixture
def fake_ml_model(db: Session) -> FakeMlModel:
    return FakeMlModel(db=db)


@pytest.fixture
def service(db, fake_ml_model) -> AdverseDrugReactionReportService:
    return build_service(db=db, ml_model=fake_ml_model)


def count_rows(db: Session) -> tuple[int, int]:
    return (
        db.query(ADRModel).count(),
        db.query(CausalityAssessmentLevelModel).count(),
    )


def test_create_gives_the_model_the_same_input_as_the_saved_row(
    db, service, fake_ml_model, adr_data
):
    result = service.create_and_predict(data=adr_data)

    saved = db.get(ADRModel, result.id)
    pd.testing.assert_frame_equal(fake_ml_model.inputs[0], expected_frame(saved))


def test_edit_gives_the_model_the_same_input_as_the_saved_row(
    db, service, fake_ml_model, adr_data
):
    created = service.create_and_predict(data=adr_data)

    service.update_and_predict(
        id=created.id, data=adr_data.model_copy(update={"rifampicin_dose_amount": 450.0})
    )

    saved = db.get(ADRModel, created.id)
    assert len(fake_ml_model.inputs) == 2
    pd.testing.assert_frame_equal(fake_ml_model.inputs[1], expected_frame(saved))
    assert fake_ml_model.inputs[1]["rifampicin_dose_amount"][0] == 450.0


def test_edit_that_changes_no_model_input_does_not_run_the_model(
    service, fake_ml_model, adr_data
):
    created = service.create_and_predict(data=adr_data)

    service.update_and_predict(
        id=created.id, data=adr_data.model_copy(update={"comments": "Only a comment."})
    )

    assert len(fake_ml_model.inputs) == 1


def test_create_runs_the_model_with_no_open_transaction(
    service, fake_ml_model, adr_data
):
    service.create_and_predict(data=adr_data)

    assert fake_ml_model.in_transaction_during_predict == [False]


def test_edit_runs_the_model_with_no_open_transaction(service, fake_ml_model, adr_data):
    created = service.create_and_predict(data=adr_data)

    service.update_and_predict(
        id=created.id, data=adr_data.model_copy(update={"rifampicin_dose_amount": 450.0})
    )

    assert fake_ml_model.in_transaction_during_predict == [False, False]


def test_create_saves_nothing_when_the_model_fails(db, adr_data):
    failing_model = FakeMlModel(db=db, error=RuntimeError("model failed"))
    service = build_service(db=db, ml_model=failing_model)

    with pytest.raises(RuntimeError, match="model failed"):
        service.create_and_predict(data=adr_data)

    assert count_rows(db) == (0, 0)


def test_edit_saves_nothing_when_the_model_fails(db, service, adr_data):
    created = service.create_and_predict(data=adr_data)
    failing_model = FakeMlModel(db=db, error=RuntimeError("model failed"))
    failing_service = build_service(db=db, ml_model=failing_model)

    with pytest.raises(RuntimeError, match="model failed"):
        failing_service.update_and_predict(
            id=created.id,
            data=adr_data.model_copy(update={"rifampicin_dose_amount": 450.0}),
        )

    saved = db.get(ADRModel, created.id)
    assert saved.rifampicin_dose_amount == 600.0
    assert count_rows(db) == (1, 1)
