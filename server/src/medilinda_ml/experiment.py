"""The experiment: choose the features and the estimator, and record the choice.

Notebook 3.3 and `python -m medilinda_ml.experiment` call `run_experiment`. It
writes `selection.json`, and the production training reads that file. Only the
training rows are used, so the test rows stay untouched until the final run.

Side effects (MLflow runs, the selection file) are in `run_experiment` and in
the functions that it calls and that name MLflow in their doc comment.
"""

import logging
from collections.abc import Iterator
from contextlib import contextmanager
from importlib.metadata import version as installed_version
from pathlib import Path
from typing import Final

import mlflow
import mlflow.data
import numpy as np
import pandas as pd
from imblearn.over_sampling import SMOTE
from imblearn.pipeline import Pipeline
from medilinda_ml.candidates import ESTIMATOR_SEED, Candidate, all_candidates
from medilinda_ml.columns import TARGET_COLUMN, TARGET_LEVELS
from medilinda_ml.data_split import (
    SPLIT_SEED,
    TEST_FRACTION,
    VALIDATION_FRACTION,
    DataSplit,
    split_dataset,
)
from medilinda_ml.evaluation import classify, headline_metrics
from medilinda_ml.experiment_rules import (
    CandidateResult,
    choose_winner,
    to_json_params,
)
from medilinda_ml.paths import DATA_DIR, SELECTION_PATH, TRACKING_DIR
from medilinda_ml.pipeline import RESAMPLING_SEED, build_pipeline, preprocessing_steps
from medilinda_ml.selection import ModelSelection, hash_data_file, write_selection
from medilinda_ml.tracking import (
    LIBRARIES_TO_RECORD,
    current_git_commit,
    portable_runs_folder,
    start_local_tracking,
)
from pydantic import BaseModel
from sklearn.feature_selection import RFECV
from sklearn.model_selection import RandomizedSearchCV, RepeatedStratifiedKFold
from sklearn.preprocessing import OrdinalEncoder
from sklearn.tree import DecisionTreeClassifier

CV_SPLITS: Final[int] = 5
CV_REPEATS: Final[int] = 3
SCORING: Final[str] = "f1_weighted"
MAX_SEARCH_DRAWS: Final[int] = 20


@contextmanager
def quiet_transformer_logs() -> Iterator[None]:
    """Side effect (logging): hide the INFO lines of each transformer inside the block.

    Every transformer logs its shape on each call, and the search calls them thousands of times.
    """
    root_logger = logging.getLogger()
    previous_level = root_logger.level
    root_logger.setLevel(logging.WARNING)
    try:
        yield
    finally:
        root_logger.setLevel(previous_level)


class ExperimentResult(BaseModel):
    """Everything the experiment found, for the notebook to show."""

    selected_features: list[str]
    candidate_results: list[CandidateResult]
    winner: CandidateResult
    selection: ModelSelection


def select_features(
    *, X_train: pd.DataFrame, y_train_encoded: np.ndarray, cv: RepeatedStratifiedKFold
) -> list[str]:
    """Return the columns that recursive feature elimination keeps.

    SMOTE is inside the estimator of the elimination, so it resamples inside each fold.
    The preprocessing is fitted once on all training rows, before the folds.
    """
    prepared = Pipeline(preprocessing_steps()).fit_transform(X_train)
    # Free-text columns (description_of_reaction) cannot be features of the model.
    prepared = prepared.select_dtypes(include=["number", "bool"])
    estimator = Pipeline(
        [
            ("smote", SMOTE(random_state=RESAMPLING_SEED)),
            ("classifier", DecisionTreeClassifier(random_state=ESTIMATOR_SEED)),
        ]
    )
    elimination = RFECV(
        estimator=estimator,
        step=1,
        min_features_to_select=1,
        cv=cv,
        scoring=SCORING,
        importance_getter="named_steps.classifier.feature_importances_",
        n_jobs=-1,
    )
    elimination.fit(prepared, y_train_encoded)
    return [str(name) for name in elimination.get_feature_names_out()]


def search_candidate(
    *,
    candidate: Candidate,
    features: list[str],
    split: DataSplit,
    y_train_encoded: np.ndarray,
    y_val_encoded: np.ndarray,
    cv: RepeatedStratifiedKFold,
) -> CandidateResult:
    """Side effect (MLflow): search the grid of one candidate, and log it as a child run.

    The search scores on the training rows. The validation rows only report.
    """
    tuned_grid = {f"classifier__{name}": values for name, values in candidate.param_grid.items()}
    draws = int(min(MAX_SEARCH_DRAWS, np.prod([len(values) for values in tuned_grid.values()])))
    search = RandomizedSearchCV(
        estimator=build_pipeline(estimator=candidate.estimator, final_columns=features),
        param_distributions=tuned_grid,
        cv=cv,
        n_iter=draws,
        scoring=SCORING,
        random_state=SPLIT_SEED,
        n_jobs=-1,
    )
    with mlflow.start_run(run_name=candidate.name, nested=True):
        search.fit(split.X_train, y_train_encoded)

        encoder = OrdinalEncoder(categories=[TARGET_LEVELS]).fit(split.y_train.to_frame())
        predicted = encoder.inverse_transform(
            search.best_estimator_.predict(split.X_val).reshape(-1, 1)
        ).ravel()
        true = encoder.inverse_transform(y_val_encoded.reshape(-1, 1)).ravel()
        validation = classify(
            true_labels=true.tolist(), predicted_labels=predicted.tolist(), labels=TARGET_LEVELS
        )
        validation_metrics = headline_metrics(split="validation", result=validation)

        result = CandidateResult(
            name=candidate.name,
            best_params=to_json_params(search_params=search.best_params_),
            cv_mean_weighted_f1=float(search.cv_results_["mean_test_score"][search.best_index_]),
            cv_std_weighted_f1=float(search.cv_results_["std_test_score"][search.best_index_]),
            validation_weighted_f1=validation_metrics["validation_f1_weighted"],
        )
        mlflow.set_tag("candidate", candidate.name)
        mlflow.log_params({f"best_{name}": value for name, value in result.best_params.items()})
        mlflow.log_metrics(
            {
                "cv_mean_f1_weighted": result.cv_mean_weighted_f1,
                "cv_std_f1_weighted": result.cv_std_weighted_f1,
                **validation_metrics,
            }
        )
        mlflow.log_dict(validation.model_dump(), "validation_result.json")
    return result


def run_experiment(
    *,
    data_path: Path = DATA_DIR / "data.csv",
    selection_path: Path = SELECTION_PATH,
    tracking_dir: Path = TRACKING_DIR,
    candidates: list[Candidate] | None = None,
    cv_splits: int = CV_SPLITS,
    cv_repeats: int = CV_REPEATS,
) -> ExperimentResult:
    """Side effect (MLflow, disk): run the experiment and write the selection file.

    One parent run (tag stage=experiment) holds one child run for each candidate.
    """
    df = pd.read_csv(data_path)
    chosen_candidates = all_candidates() if candidates is None else candidates

    start_local_tracking(tracking_dir=tracking_dir)
    split = split_dataset(df=df)
    encoder = OrdinalEncoder(categories=[TARGET_LEVELS])
    y_train_encoded = encoder.fit_transform(split.y_train.to_frame()).ravel()
    y_val_encoded = encoder.transform(split.y_val.to_frame()).ravel()
    cv = RepeatedStratifiedKFold(n_splits=cv_splits, n_repeats=cv_repeats, random_state=SPLIT_SEED)

    with quiet_transformer_logs(), mlflow.start_run(run_name="experiment") as parent_run:
        mlflow.set_tags(
            {
                "stage": "experiment",
                "git_commit": current_git_commit() or "unknown",
                **{f"library.{name}": installed_version(name) for name in LIBRARIES_TO_RECORD},
            }
        )
        mlflow.log_input(
            mlflow.data.from_pandas(
                df, source=str(data_path), name=data_path.name, targets=TARGET_COLUMN
            ),
            context="experiment",
        )
        mlflow.log_params(
            {
                "split_seed": SPLIT_SEED,
                "test_fraction": TEST_FRACTION,
                "validation_fraction": VALIDATION_FRACTION,
                "cv_splits": cv_splits,
                "cv_repeats": cv_repeats,
                "scoring": SCORING,
                "train_rows": len(split.X_train),
                "validation_rows": len(split.X_val),
                "candidates": ",".join(candidate.name for candidate in chosen_candidates),
            }
        )

        features = select_features(X_train=split.X_train, y_train_encoded=y_train_encoded, cv=cv)
        mlflow.log_param("n_selected_features", len(features))
        mlflow.log_dict({"features": features}, "selected_features.json")

        results = [
            search_candidate(
                candidate=candidate,
                features=features,
                split=split,
                y_train_encoded=y_train_encoded,
                y_val_encoded=y_val_encoded,
                cv=cv,
            )
            for candidate in chosen_candidates
        ]
        mlflow.log_dict([result.model_dump() for result in results], "candidate_results.json")

        winner = choose_winner(results=results)
        mlflow.set_tag("winner", winner.name)
        mlflow.log_metric("winner_cv_mean_f1_weighted", winner.cv_mean_weighted_f1)

        selection = ModelSelection(
            estimator=winner.name,
            params=winner.best_params,
            features=features,
            data_sha256=hash_data_file(path=data_path),
            split_seed=SPLIT_SEED,
            experiment_run_id=parent_run.info.run_id,
            cv_weighted_f1=winner.cv_mean_weighted_f1,
        )
        write_selection(path=selection_path, selection=selection)
        mlflow.log_artifact(str(selection_path))

    return ExperimentResult(
        selected_features=features,
        candidate_results=results,
        winner=winner,
        selection=selection,
    )


if __name__ == "__main__":
    with portable_runs_folder():
        run_experiment()
