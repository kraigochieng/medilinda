import datetime
import json
from typing import Any, List, Tuple

import joblib
import numpy as np
import pandas as pd
from shap import Explainer
from sklearn.base import BaseEstimator
from sklearn.preprocessing import OneHotEncoder, OrdinalEncoder


def safe_date_parse(value: Any):
    try:
        if pd.isna(value):
            return None
        if isinstance(value, datetime.datetime):
            return value.date()
        return pd.to_datetime(value).date()
    except Exception:
        return None


# Utility functions
def get_ml_model(path: str) -> BaseEstimator:
    """Load the trained ML model."""
    return joblib.load(path)


def get_scalers(path: str) -> BaseEstimator:
    """Load the trained ML model."""
    return joblib.load(path)


def get_encoders(path: str) -> Tuple[OneHotEncoder, OrdinalEncoder]:
    """Load the one-hot and ordinal encoders."""
    one_hot_encoder = joblib.load(f"{path}/one_hot_encoder.pkl")
    ordinal_encoder = joblib.load(f"{path}/ordinal_encoder.pkl")
    return one_hot_encoder, ordinal_encoder


def get_column_metadata(path: str) -> dict:
    """Return list of categorical fields used for encoding."""
    """Load the one-hot and ordinal encoders."""

    with open(path, "r") as f:
        column_metadata = json.load(f)

    categorical_columns = column_metadata["categorical_columns"]
    numerical_columns = column_metadata["numerical_columns"]
    date_columns = column_metadata["date_columns"]
    boolean_columns = column_metadata["boolean_columns"]
    prediction_columns = column_metadata["prediction_columns"]
    columns_to_drop = column_metadata["columns_to_drop"]

    return {
        "categorical_columns": categorical_columns,
        "numerical_columns": numerical_columns,
        "date_columns": date_columns,
        "boolean_columns": boolean_columns,
        "prediction_columns": prediction_columns,
        "columns_to_drop": columns_to_drop,
    }


def input_to_prediction_format(
    input_df: pd.DataFrame, column_metadata: dict, scalers_path: str, encoders_path: str
) -> pd.DataFrame:
    """
    This function returns for a proper dataframe for the ML model and SHAP model
    """

    categorical_columns = column_metadata["categorical_columns"]
    numerical_columns = column_metadata["numerical_columns"]
    date_columns = column_metadata["date_columns"]
    boolean_columns = column_metadata["boolean_columns"]
    prediction_columns = column_metadata["prediction_columns"]
    columns_to_drop = column_metadata["columns_to_drop"]

    # Create all the columns not originally in dataset
    ## Num suspected drugs
    input_df["num_suspected_drugs"] = input_df[boolean_columns].sum(axis=1)

    for column in categorical_columns:
        input_df[column] = input_df[column].astype("category")

    ## Patient Age and Patient Date of Birth
    date_columns_without_created_at = date_columns
    date_columns_without_created_at.remove("created_at")

    for column in date_columns:
        input_df[column] = pd.to_datetime(input_df[column], errors="coerce")

    today = pd.to_datetime("today")

    missing_age_mask = (
        input_df["patient_age"].isnull() & input_df["patient_date_of_birth"].notnull()
    )

    input_df.loc[missing_age_mask, "patient_age"] = (
        today - input_df.loc[missing_age_mask, "patient_date_of_birth"]
    ).dt.days // 365

    input_df["patient_age"] = input_df["patient_age"].fillna(
        input_df["patient_age"].median()
    )

    ## Patient BMI
    input_df["patient_bmi"] = input_df["patient_weight_kg"] / (
        input_df["patient_height_cm"] * input_df["patient_height_cm"]
    )

    ## Drug columns
    drug_names = ["rifampicin", "isoniazid", "pyrazinamide", "ethambutol"]

    for drug in drug_names:
        start_col = f"{drug}_start_to_onset_days"
        stop_col = f"{drug}_stop_to_onset_days"
        start_stop_col = f"{drug}_start_stop_difference"

        input_df[start_col] = (
            input_df["date_of_onset_of_reaction"] - input_df[f"{drug}_start_date"]
        ).dt.days
        input_df[stop_col] = (
            input_df["date_of_onset_of_reaction"] - input_df[f"{drug}_stop_date"]
        ).dt.days
        input_df[start_stop_col] = (
            input_df[f"{drug}_stop_date"] - input_df[f"{drug}_start_date"]
        ).dt.days

    # Drop date columns
    input_df = input_df.drop(columns=date_columns)

    input_df = input_df.drop(columns=columns_to_drop)

    # Fill null valuea
    input_df[numerical_columns] = input_df[numerical_columns].fillna(-1)

    # Scale numerical columns
    minmax_scaler = get_scalers(scalers_path)
    scaled_numericals = minmax_scaler.transform(input_df[numerical_columns])
    scaled_numericals_df = pd.DataFrame(scaled_numericals, columns=numerical_columns)

    # Encode categorical columns

    one_hot_encoder, _ = get_encoders(encoders_path)

    cat_encoded = one_hot_encoder.transform(input_df[categorical_columns])
    cat_encoded_df = pd.DataFrame(
        cat_encoded, columns=one_hot_encoder.get_feature_names_out(categorical_columns)
    )

    # Merge all features
    final_input_df = pd.concat(
        [
            cat_encoded_df,
            input_df[boolean_columns].reset_index(drop=True),
            scaled_numericals_df,
        ],
        axis=1,
    )

    # Reorder to match training time
    final_input_df = final_input_df[prediction_columns]

    return final_input_df


def format_feature_values(feature_values: List[any], scalers_path: str) -> List[any]:
    minmax_scaler = get_scalers(scalers_path)

    reversed_values = []

    for i, value in enumerate(feature_values):
        # Handle logical encoding: 0 → False, 1 → True, -1 → None
        if value == 0:
            reversed_values.append(False)
        elif value == 1:
            reversed_values.append(True)

        # Reverse min-max scaling for decimal floats
        elif isinstance(value, float) and not value.is_integer():
            min_val = minmax_scaler.data_min_[i]
            max_val = minmax_scaler.data_max_[i]
            original = round(value * (max_val - min_val) + min_val)
            if original == -1:
                reversed_values.append(None)
            else:
                reversed_values.append(original)

        # Leave all other values as-is
        else:
            reversed_values.append(value)

    return reversed_values


def get_shap_values(shap_values: Explainer):
    base_values = list(shap_values.base_values[0])
    shap_values_matrix = shap_values.values[0].tolist()
    shap_values_sum_per_class = np.sum(shap_values.values[0], axis=0).tolist()
    shap_values_and_base_values_sum_per_class = list(
        np.sum(shap_values.values[0], axis=0) + shap_values.base_values[0]
    )

    return {
        "base_values": base_values,
        "shap_values_matrix": shap_values_matrix,
        "shap_values_sum_per_class": shap_values_sum_per_class,
        "shap_values_and_base_values_sum_per_class": shap_values_and_base_values_sum_per_class,
    }
