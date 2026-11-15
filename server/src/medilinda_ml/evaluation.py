"""Pure functions that measure a model for the experiment run.

They return plain numbers and tables. The training code logs them to MLflow.
"""

import numpy as np
from pydantic import BaseModel
from sklearn.metrics import classification_report, confusion_matrix


class ClassificationResult(BaseModel):
    """The classification report and the confusion matrix of one split."""

    rows: int
    labels: list[str]
    report: dict[str, float | dict[str, float]]
    confusion_matrix: list[list[int]]


def classify(
    *, true_labels: list[str], predicted_labels: list[str], labels: list[str]
) -> ClassificationResult:
    """Measure the predictions of one split against its true labels."""
    return ClassificationResult(
        rows=len(true_labels),
        labels=labels,
        report=classification_report(
            true_labels,
            predicted_labels,
            labels=labels,
            output_dict=True,
            zero_division=0,
        ),
        confusion_matrix=confusion_matrix(
            true_labels, predicted_labels, labels=labels
        ).tolist(),
    )


def headline_metrics(*, split: str, result: ClassificationResult) -> dict[str, float]:
    """The metrics to log for one split, named `<split>_<metric>`."""
    weighted = result.report["weighted avg"]
    macro = result.report["macro avg"]
    assert isinstance(weighted, dict) and isinstance(macro, dict)

    return {
        f"{split}_accuracy": float(result.report["accuracy"]),
        f"{split}_f1_weighted": weighted["f1-score"],
        f"{split}_precision_weighted": weighted["precision"],
        f"{split}_recall_weighted": weighted["recall"],
        f"{split}_f1_macro": macro["f1-score"],
    }


def max_additivity_error(
    *, shap_values: np.ndarray, base_values: np.ndarray, model_output: np.ndarray
) -> float:
    """The largest gap between the SHAP sum and the model output.

    For each row and class, the SHAP values plus the base value must add up to the
    output of the model. Shapes: shap_values (rows, features, classes), base_values
    and model_output (rows, classes).
    """
    reconstructed = shap_values.sum(axis=1) + base_values
    return float(np.abs(reconstructed - model_output).max())
