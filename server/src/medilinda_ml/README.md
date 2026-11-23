# Medilinda-ML 💊

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A complete machine learning pipeline to predict the causality of Adverse Drug Reactions (ADRs) from patient and medication data. This package provides tools for data preprocessing, feature engineering, model training, and evaluation, with seamless MLflow integration for experiment tracking.

## Overview

The goal of Medilinda-ML is to provide a reproducible and easy-to-use system for assessing the likelihood that a suspected drug is the cause of an adverse reaction. The pipeline is built with `scikit-learn` and handles common challenges in clinical data, such as missing values and class imbalance (using SMOTE).

## Features

-   **End-to-End Pipeline**: From raw data to a trained model.
-   **Feature Engineering**: Automatically calculates features like patient BMI, drug administration duration, and more.
-   **Class Imbalance Handling**: Uses SMOTE to create a balanced dataset for training.
-   **Hyperparameter Tuning**: Leverages `RandomizedSearchCV` to find the best model configuration.
-   **Experiment Tracking**: Integrated with MLflow to log parameters, metrics, and models.

## Where the code lives

The Python package `medilinda_ml` is part of the server. It is in `server/src/medilinda_ml/`.
The training data is in `data/` and the notebooks are in `notebooks/`. The Docker image leaves both out.
Nothing publishes the package to PyPI.

## Data

The training data is synthetic. A sampler builds each case in causal order, and the WHO-UMC rules give the level
(issue #164, `docs/synthetic-data-report.md`). Make the data from the `server` folder:

```bash
PYTHONPATH=src uv run python -m medilinda_ml.data_generation --rows 30000 --seed 42 \
    --output src/medilinda_ml/data/data_who_umc.csv.gz
PYTHONPATH=src uv run python -m medilinda_ml.dataset_validation \
    --dataset src/medilinda_ml/data/data_who_umc.csv.gz --output ../docs/synthetic-data-report.md
```

The same seed gives the same bytes. The command writes a second file, `data_who_umc_diagnostics.csv.gz`, with the clean
rule label, the latent cause and the regimen. Training must never read it, and the loader refuses a frame that has these columns.
The older `data/data.csv` is the data of the first generator (the label came first). Nothing trains on it now.

## Feature sets

- `app`: the columns that the app collects today. The production model uses this set.
- `full`: the app columns and the new report fields of decision DR-8 (history, other medicines, labs, eye exam). The app does not collect them yet (issue #174).

## Experiment

The experiment picks the model that goes to production. Run it from the `server` folder:

```bash
PYTHONPATH=src uv run --group train python -m medilinda_ml.experiment --feature-set app \
    --cv-splits 3 --cv-repeats 1 \
    --candidates decision_tree,ada_boost,logistic_regression,random_forest,gradient_boosting,naive_bayes
```

Without arguments it uses all eight candidates, 5-fold cross-validation with 3 repeats, and the feature set `app`.
The SVM and the k-nearest-neighbours candidates are slow on 30,000 rows, so the run of 2026-11-24 left them out.
The experiment uses the training rows only. It never scores the test rows.
It logs each candidate as a run in MLflow (`mlruns/`, experiment `medilinda-causality`).
It writes `selection.json` (or the path of `--selection-path`) with the winner, its parameters, its features, the feature set and the hash of the data file.
`selection_full.json` is the selection of the `full` feature set.

To look at the runs, start the MLflow interface: `uv run --group train mlflow ui --backend-store-uri mlruns`.

## Training

```bash
uv sync --group train
PYTHONPATH=src uv run --group train python -m medilinda_ml.modeling.train_model
```

The training reads `selection.json`. It stops if the hash of the data file differs from the hash in `selection.json`. Run the experiment again then.
It trains the selected estimator once, with the selected params and features. It does not search.
It evaluates once on the held-out test rows, logs a run with the tag `stage=production`, and writes a new version folder in `server/models/`.
Then write the golden file: `PYTHONPATH=src uv run python -m medilinda_ml.golden models/<version folder>`.
The server loads the version that `models/LATEST` names.

## Results

`python -m medilinda_ml.result_report --output ../docs/model-results.md` trains the selections and reports the held-out results,
the effect of label noise, and the recall of "certain". Read `docs/model-results.md` before you deploy a model.
The scores show how well a model learns the generator. They do not show clinical accuracy.

## Notebooks

The notebooks import `medilinda_ml`. Set `PYTHONPATH` to the `server/src` folder before you start the notebook kernel.
Install the `train` group first: `cd server && uv sync --group train`.
The `train` group has `ipykernel` and `faker`. It has no Jupyter server, so use your editor or install one.

`notebooks/0.2-kraig-data_generation.ipynb` is the first generator (the label came first). It is kept for the history. Use `medilinda_ml.data_generation` instead.

## License

This project is licensed under the MIT License. See the `LICENSE` file for more details.
