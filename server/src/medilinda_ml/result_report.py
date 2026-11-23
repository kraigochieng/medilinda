"""Train a selection once and report its results, including the effect of label noise.

This is a report, not the production training. It does not save a model. It reads a selection file,
fits the chosen estimator on the training rows of a generated dataset, and measures it on the held-out
test rows against the noisy label (what the model learned) and against the clean rule label (what
the rules say). The clean label comes from the diagnostics table, never from training.

Run from the server folder, for example:

    PYTHONPATH=src uv run --group train python -m medilinda_ml.result_report --output ../docs/model-results.md
"""

import argparse
from pathlib import Path
from typing import Final

import pandas as pd
from medilinda_ml.candidates import candidate_named
from medilinda_ml.columns import TARGET_COLUMN, TARGET_LEVELS
from medilinda_ml.data_generation import generate_tables
from medilinda_ml.data_split import split_dataset
from medilinda_ml.evaluation import ClassificationResult, classify
from medilinda_ml.paths import PACKAGE_DIR
from medilinda_ml.pipeline import build_pipeline
from medilinda_ml.selection import ModelSelection, read_selection
from medilinda_ml.training_data import FeatureSet, prepare_training_frame
from pydantic import BaseModel, ConfigDict
from sklearn.preprocessing import OrdinalEncoder

DATE_FEATURE_MARKERS: Final[list[str]] = ["start_to_onset", "stop_to_onset", "start_stop_difference"]


class ScenarioResult(BaseModel):
    """The held-out results of one scenario."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    name: str
    feature_count: int
    test_rows: int
    against_noisy_label: ClassificationResult
    against_clean_label: ClassificationResult


def constant_baseline_weighted_f1(*, labels: list[str]) -> float:
    """Return the weighted F1 of a model that always predicts the most common level. Pure."""
    most_common = max(set(labels), key=labels.count)
    result = classify(true_labels=labels, predicted_labels=[most_common] * len(labels), labels=TARGET_LEVELS)
    weighted = result.report["weighted avg"]
    assert isinstance(weighted, dict)
    return float(weighted["f1-score"])


def evaluate_scenario(
    *,
    name: str,
    selection: ModelSelection,
    dataset: pd.DataFrame,
    diagnostics: pd.DataFrame,
    drop_date_features: bool = False,
) -> ScenarioResult:
    """Side effect (CPU): fit the selected estimator on the training rows and measure it on the test rows."""
    frame = prepare_training_frame(frame=dataset, feature_set=selection.feature_set)
    mask = dataset[TARGET_COLUMN].isin(TARGET_LEVELS).to_numpy()
    clean_labels = diagnostics.loc[mask, "causality_by_rule"].reset_index(drop=True)
    split = split_dataset(df=frame)
    features = [
        feature
        for feature in selection.features
        if not (drop_date_features and any(marker in feature for marker in DATE_FEATURE_MARKERS))
    ]
    encoder = OrdinalEncoder(categories=[TARGET_LEVELS])
    train_labels = encoder.fit_transform(split.y_train.to_frame()).ravel()
    pipeline = build_pipeline(
        estimator=candidate_named(name=selection.estimator).estimator.set_params(**selection.params),
        final_columns=features,
        include_history=selection.feature_set == "full",
    )
    pipeline.fit(split.X_train, train_labels)
    predicted = encoder.inverse_transform(pipeline.predict(split.X_test).reshape(-1, 1)).ravel().tolist()
    return ScenarioResult(
        name=name,
        feature_count=len(features),
        test_rows=len(split.X_test),
        against_noisy_label=classify(true_labels=split.y_test.tolist(), predicted_labels=predicted, labels=TARGET_LEVELS),
        against_clean_label=classify(
            true_labels=clean_labels.loc[split.X_test.index].tolist(), predicted_labels=predicted, labels=TARGET_LEVELS
        ),
    )


def _row(*, result: ScenarioResult) -> str:
    """Return one table row: weighted F1 and the recall of each level, against the clean label."""
    clean = result.against_clean_label.report
    noisy = result.against_noisy_label.report
    weighted_noisy = noisy["weighted avg"]
    weighted_clean = clean["weighted avg"]
    assert isinstance(weighted_noisy, dict) and isinstance(weighted_clean, dict)
    recalls = []
    for level in TARGET_LEVELS:
        level_report = clean[level]
        assert isinstance(level_report, dict)
        recalls.append(f"{level_report['recall']:.2f}")
    return (
        f"| {result.name} | {result.feature_count} | {weighted_noisy['f1-score']:.3f} | {weighted_clean['f1-score']:.3f} | "
        + " | ".join(recalls)
        + " |"
    )


def _confusion_table(*, result: ScenarioResult) -> str:
    """Return the confusion matrix against the clean label as a Markdown table (rows: true, columns: predicted)."""
    header = "| true \\ predicted | " + " | ".join(TARGET_LEVELS) + " |\n|---|" + "---|" * len(TARGET_LEVELS)
    lines = [
        f"| {level} | " + " | ".join(str(count) for count in counts) + " |"
        for level, counts in zip(TARGET_LEVELS, result.against_clean_label.confusion_matrix, strict=True)
    ]
    return header + "\n" + "\n".join(lines)


def render_markdown(
    *, scenarios: list[ScenarioResult], noise_scenarios: list[ScenarioResult], baseline: float, rows: int
) -> str:
    """Return the results as Markdown text. Pure."""
    main_rows = "\n".join(_row(result=result) for result in scenarios)
    noise_rows = "\n".join(_row(result=result) for result in noise_scenarios)
    confusion = "\n\n".join(f"**{result.name}**\n\n{_confusion_table(result=result)}" for result in scenarios)
    test_rows = scenarios[0].test_rows
    return f"""# Results of the models on the synthetic data

Generated by `python -m medilinda_ml.result_report`. Data: {rows} generated rows, test split of {test_rows} rows (only the four levels that the model predicts).
The data is synthetic. The scores show how well a model learns the rules of the generator. They do not show clinical accuracy.
Issue #164 explains the design. The columns of recall are against the **clean** rule label.

## Models

Weighted F1 is shown against the label that the model learned (with noise) and against the clean rule label.
The constant model always predicts the most common level. Its weighted F1 on the noisy label is {baseline:.3f}.

| Scenario | Features | Weighted F1 (noisy label) | Weighted F1 (clean label) | Recall certain | Recall likely | Recall possible | Recall unlikely |
|---|---|---|---|---|---|---|---|
{main_rows}

## Effect of label noise

The same cases with a different share of moved labels (decision DR-6). Feature set "full". The test rows are the same cases in each row.

| Scenario | Features | Weighted F1 (noisy label) | Weighted F1 (clean label) | Recall certain | Recall likely | Recall possible | Recall unlikely |
|---|---|---|---|---|---|---|---|
{noise_rows}

## Confusion matrices (against the clean label)

{confusion}
"""


def main() -> None:
    """Side effect (disk, CPU): evaluate the scenarios and write the Markdown report."""
    parser = argparse.ArgumentParser(description="Report the results of the selected models (issue #164).")
    parser.add_argument("--app-selection", type=Path, default=PACKAGE_DIR / "selection.json", help="the selection of the production model")
    parser.add_argument("--full-selection", type=Path, default=PACKAGE_DIR / "selection_full.json", help="the selection with the new report fields")
    parser.add_argument("--rows", type=int, default=30_000, help="the rows to generate, for example 30000")
    parser.add_argument("--seed", type=int, default=42, help="the seed, for example 42")
    parser.add_argument("--output", type=Path, required=True, help="the Markdown report to write")
    arguments = parser.parse_args()

    app_selection = read_selection(path=arguments.app_selection)
    full_selection = read_selection(path=arguments.full_selection)
    dataset, diagnostics = generate_tables(rows=arguments.rows, seed=arguments.seed, label_noise=0.05)
    scenarios = [
        evaluate_scenario(name="App fields (production model)", selection=app_selection, dataset=dataset, diagnostics=diagnostics),
        evaluate_scenario(name="App fields and the new fields", selection=full_selection, dataset=dataset, diagnostics=diagnostics),
        evaluate_scenario(
            name="App fields and the new fields, without the date features",
            selection=full_selection,
            dataset=dataset,
            diagnostics=diagnostics,
            drop_date_features=True,
        ),
    ]
    noise_scenarios: list[ScenarioResult] = []
    for rate in (0.0, 0.05, 0.10):
        noisy_dataset, noisy_diagnostics = generate_tables(rows=arguments.rows, seed=arguments.seed, label_noise=rate)
        noise_scenarios.append(
            evaluate_scenario(name=f"Noise {rate:.0%}", selection=full_selection, dataset=noisy_dataset, diagnostics=noisy_diagnostics)
        )
    labels = dataset.loc[dataset[TARGET_COLUMN].isin(TARGET_LEVELS), TARGET_COLUMN].tolist()
    arguments.output.write_text(
        render_markdown(
            scenarios=scenarios,
            noise_scenarios=noise_scenarios,
            baseline=constant_baseline_weighted_f1(labels=labels),
            rows=arguments.rows,
        )
    )


if __name__ == "__main__":
    main()
