import numpy as np
import pytest
from medilinda_ml.evaluation import classify, headline_metrics, max_additivity_error


def test_classify_counts_rows_and_builds_the_confusion_matrix():
    result = classify(
        true_labels=["a", "a", "b", "b"],
        predicted_labels=["a", "b", "b", "b"],
        labels=["a", "b"],
    )

    assert result.rows == 4
    assert result.confusion_matrix == [[1, 1], [0, 2]]
    assert result.report["accuracy"] == pytest.approx(0.75)


def test_classify_keeps_a_label_that_never_appears():
    result = classify(
        true_labels=["a", "a"], predicted_labels=["a", "a"], labels=["a", "b"]
    )

    assert result.confusion_matrix == [[2, 0], [0, 0]]
    assert result.report["b"]["support"] == 0


def test_classify_refuses_labels_of_different_lengths():
    with pytest.raises(ValueError):
        classify(true_labels=["a"], predicted_labels=["a", "b"], labels=["a", "b"])


def test_headline_metrics_name_each_metric_after_its_split():
    result = classify(
        true_labels=["a", "a", "b", "b"],
        predicted_labels=["a", "b", "b", "b"],
        labels=["a", "b"],
    )

    metrics = headline_metrics(split="test", result=result)

    assert set(metrics) == {
        "test_accuracy",
        "test_f1_weighted",
        "test_precision_weighted",
        "test_recall_weighted",
        "test_f1_macro",
    }
    assert metrics["test_accuracy"] == pytest.approx(0.75)
    assert metrics["test_recall_weighted"] == pytest.approx(0.75)


def test_max_additivity_error_is_zero_when_the_values_add_up():
    shap_values = np.array([[[0.1, -0.1], [0.2, -0.2]]])
    base_values = np.array([[0.5, 0.5]])
    model_output = np.array([[0.8, 0.2]])

    assert max_additivity_error(
        shap_values=shap_values, base_values=base_values, model_output=model_output
    ) == pytest.approx(0.0)


def test_max_additivity_error_gives_the_largest_gap():
    shap_values = np.array([[[0.1, -0.1]]])
    base_values = np.array([[0.5, 0.5]])
    model_output = np.array([[0.6, 0.1]])

    assert max_additivity_error(
        shap_values=shap_values, base_values=base_values, model_output=model_output
    ) == pytest.approx(0.3)
