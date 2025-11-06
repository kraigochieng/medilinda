from datetime import date, datetime
from typing import TypedDict

import numpy as np
import pandas as pd
from shap import Explanation


class ShapValues(TypedDict):
    base_values: list
    shap_values_matrix: list
    shap_values_sum_per_class: list
    shap_values_and_base_values_sum_per_class: list


def get_shap_values(shap_values: Explanation) -> ShapValues:
    base_values: list = list(shap_values.base_values[0])
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


def safe_date_parse(date_str):
    """
    Safely parses a date string into a datetime.date object.
    Returns None if the input is empty, invalid, or causes an error.
    """
    if pd.isna(date_str) or not date_str:
        return None
    try:
        # pd.to_datetime is flexible and can handle many formats
        return pd.to_datetime(date_str).date()
    except (ValueError, TypeError):
        return None


def format_dataframe_for_model(
    df: pd.DataFrame,
    model_cols: list[str],
    numeric_cols: list[str],
    bool_cols: list[str],
    string_cols: list[str],
) -> pd.DataFrame:
    """
    Formats a DataFrame to exactly match the MLflow model's schema.
    """
    # Work on a copy to avoid changing the original DataFrame
    formatted_df = df.copy()

    for col in model_cols:
        if col not in formatted_df.columns:
            formatted_df[col] = None

    formatted_df = formatted_df[model_cols]

    # Convert numeric columns to float, coercing errors to NaN
    for col in numeric_cols:
        if col in formatted_df.columns:
            numeric_series = pd.to_numeric(formatted_df[col], errors="coerce")
            formatted_df[col] = numeric_series.astype("float64")

    # Convert boolean columns
    for col in bool_cols:
        if col in formatted_df.columns:
            formatted_df[col] = formatted_df[col].astype(bool)

    # Convert specified columns (like dates) to strings
    for col in string_cols:
        if col in formatted_df.columns:
            # Replace Pandas' 'Not a Time' representation before converting to string
            formatted_df[col] = formatted_df[col].astype(str).replace("NaT", "None")

    return formatted_df


def make_json_serializable(item):
    """
    Recursively converts an item to be JSON serializable.
    Handles lists, dicts, numpy types, and date/datetime objects.
    """
    if isinstance(item, (list, tuple, np.ndarray)):
        # If it's a list, recurse on its items
        return [make_json_serializable(i) for i in item]

    if isinstance(item, dict):
        # If it's a dict, recurse on its values
        return {k: make_json_serializable(v) for k, v in item.items()}

    if isinstance(item, (np.floating, np.float64)):
        # Convert numpy floats to native Python floats
        return float(item)

    if isinstance(item, (np.integer, np.int64, np.int32)):
        # Convert numpy integers to native Python ints
        return int(item)

    if isinstance(item, (np.bool_)):
        # Convert numpy bools to native Python bools
        return bool(item)

    if isinstance(item, (date, datetime)):
        # Convert date/datetime objects to ISO strings
        return item.isoformat()

    if pd.isna(item):
        # Convert Pandas NaT/NaN to None (which is JSON-null)
        return None

    # Otherwise, assume it's already serializable (str, int, float, bool, None)
    return item


# Columns that MUST be numbers (double)
numeric_cols = [
    "patient_age",
    "patient_weight_kg",
    "patient_height_cm",
    "rifampicin_dose_amount",
    "rifampicin_frequency_number",
    "isoniazid_dose_amount",
    "isoniazid_frequency_number",
    "pyrazinamide_dose_amount",
    "pyrazinamide_frequency_number",
    "ethambutol_dose_amount",
    "ethambutol_frequency_number",
]


# Columns that MUST be booleans
bool_cols = [
    "rifampicin_suspected",
    "isoniazid_suspected",
    "pyrazinamide_suspected",
    "ethambutol_suspected",
]
model_cols = [
    "patient_name",
    "inpatient_or_outpatient_number",
    "patient_date_of_birth",
    "patient_age",
    "patient_address",
    "ward_or_clinic",
    "patient_gender",
    "known_allergy",
    "pregnancy_status",
    "patient_weight_kg",
    "patient_height_cm",
    "date_of_onset_of_reaction",
    "description_of_reaction",
    "rifampicin_suspected",
    "rifampicin_start_date",
    "rifampicin_stop_date",
    "rifampicin_dose_amount",
    "rifampicin_frequency_number",
    "rifampicin_route",
    "rifampicin_batch_no",
    "rifampicin_manufacturer",
    "isoniazid_suspected",
    "isoniazid_start_date",
    "isoniazid_stop_date",
    "isoniazid_dose_amount",
    "isoniazid_frequency_number",
    "isoniazid_route",
    "isoniazid_batch_no",
    "isoniazid_manufacturer",
    "pyrazinamide_suspected",
    "pyrazinamide_start_date",
    "pyrazinamide_stop_date",
    "pyrazinamide_dose_amount",
    "pyrazinamide_frequency_number",
    "pyrazinamide_route",
    "pyrazinamide_batch_no",
    "pyrazinamide_manufacturer",
    "ethambutol_suspected",
    "ethambutol_start_date",
    "ethambutol_stop_date",
    "ethambutol_dose_amount",
    "ethambutol_frequency_number",
    "ethambutol_route",
    "ethambutol_batch_no",
    "ethambutol_manufacturer",
    "dechallenge",
    "rechallenge",
    "severity",
    "is_serious",
    "criteria_for_seriousness",
    "action_taken",
    "outcome",
    "created_at",
]
# Columns (like dates) that MUST be strings
string_cols = [
    "patient_date_of_birth",
    "date_of_onset_of_reaction",
    "rifampicin_start_date",
    "rifampicin_stop_date",
    "isoniazid_start_date",
    "isoniazid_stop_date",
    "pyrazinamide_start_date",
    "pyrazinamide_stop_date",
    "ethambutol_start_date",
    "ethambutol_stop_date",
    "created_at",
]
