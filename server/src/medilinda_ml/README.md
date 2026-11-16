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

## Training

Run the commands from the `server` folder:

```bash
uv sync --group train
PYTHONPATH=src uv run python -m medilinda_ml.modeling.train_model
```

The training code reads `data/data.csv` in this folder.
It writes a new version folder in `server/models/`. See the README of the repository for the layout.

## Experiment

The experiment picks the model that goes to production. Run it from the `server` folder:

```bash
PYTHONPATH=src uv run --group train python -m medilinda_ml.experiment
```

Notebook `notebooks/3.3-kraig-model_creation.ipynb` runs the same function.
The experiment tries 8 candidates with cross-validation on the training rows only.
It never scores the test rows.
It logs each candidate as a run in MLflow (`mlruns/`, experiment `medilinda-causality`).
It writes `selection.json` with the winner, its parameters, its features and the hash of `data/data.csv`.

To look at the runs, start the MLflow interface: `uv run --group train mlflow ui --backend-store-uri mlruns`.

## Notebooks

The notebooks import `medilinda_ml`. Set `PYTHONPATH` to the `server/src` folder before you start the notebook kernel.
Install the `train` group first: `cd server && uv sync --group train`.
The `train` group has `ipykernel` and `faker`. It has no Jupyter server, so use your editor or install one.

`notebooks/0.2-kraig-data_generation.ipynb` makes synthetic data with a fixed seed and a fixed date.
It writes `data/data_seed42.csv`. It does not change `data/data.csv`, the file that the training uses.

## License

This project is licensed under the MIT License. See the `LICENSE` file for more details.
