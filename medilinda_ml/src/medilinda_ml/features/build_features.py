import io
import logging
from typing import List, Union

import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.preprocessing import MinMaxScaler, OneHotEncoder


def build_features(df: pd.DataFrame, boolean_columns: list[str]) -> pd.DataFrame:
    df["patient_bmi"] = df["patient_weight_kg"] / ((df["patient_height_cm"] / 100) ** 2)

    today = pd.to_datetime("today")  # Current date for age calculation
    missing_age_mask = (
        df["patient_age"].isnull() & df["patient_date_of_birth"].notnull()
    )  # Calculate age only where it's missing and dob is available

    df.loc[missing_age_mask, "patient_age"] = (
        today - df.loc[missing_age_mask, "patient_date_of_birth"]
    ).dt.days // 365

    df["patient_age"] = df["patient_age"].fillna(
        df["patient_age"].median()
    )  # Now fill any remaining missing ages (where dob was also missing) with median

    # Define drug prefixes for iteration
    drug_names = ["rifampicin", "isoniazid", "pyrazinamide", "ethambutol"]

    # Compute date differences in days for each drug
    for drug in drug_names:
        start_col = f"{drug}_start_to_onset_days"
        stop_col = f"{drug}_stop_to_onset_days"
        start_stop_col = f"{drug}_start_stop_difference"

        df[start_col] = (
            df["date_of_onset_of_reaction"] - df[f"{drug}_start_date"]
        ).dt.days
        df[stop_col] = (
            df["date_of_onset_of_reaction"] - df[f"{drug}_stop_date"]
        ).dt.days
        df[start_stop_col] = (
            df[f"{drug}_stop_date"] - df[f"{drug}_start_date"]
        ).dt.days

    df["num_suspected_drugs"] = df[boolean_columns].sum(axis=1)

    return df


def drop_unnecessary_columns(
    df: pd.DataFrame, columns_to_drop: list[str]
) -> pd.DataFrame:
    df.drop(columns=columns_to_drop)

    return df


class PatientAgeImputer(BaseEstimator, TransformerMixin):
    def __init__(self, verbose: bool = True):
        self.verbose = verbose

        if self.verbose:
            logging.info(f"[{self.__class__.__name__}] Transformer initialized.")

    def fit(self, X: pd.DataFrame, y=None):
        return self

    def transform(self, X: pd.DataFrame, y=None) -> pd.DataFrame:
        if self.verbose:
            logging.info(f"\n{'=' * 20} [{self.__class__.__name__}: Input] {'=' * 20}")
            logging.info(f"Shape: {X.shape}")
            logging.info(f"Columns: {X.columns.tolist()}")
            s = io.StringIO()
            X.info(buf=s)
            # # logging.info(f"df.info():\n{s.getvalue()}")
            logging.info(f"{'=' * 50}\n")

        df = X.copy()

        # Current date for age calculation
        today = pd.to_datetime("today")

        # Calculate age only where it's missing and dob is available
        missing_age_mask = (
            df["patient_age"].isnull() & df["patient_date_of_birth"].notnull()
        )

        df.loc[missing_age_mask, "patient_age"] = (
            today - df.loc[missing_age_mask, "patient_date_of_birth"]
        ).dt.days // 365

        # Convert age column to numeric before calculating median
        df["patient_age"] = pd.to_numeric(df["patient_age"], errors="coerce")

        # Now fill any remaining missing ages (where dob was also missing) with median
        df["patient_age"] = df["patient_age"].fillna(df["patient_age"].median())

        # Explicitly convert the age column to integer type
        df["patient_age"] = df["patient_age"].astype(int)

        if self.verbose:
            logging.info(f"\n{'-' * 20} [{self.__class__.__name__}: Output] {'-' * 20}")
            logging.info(f"Shape: {df.shape}")
            logging.info(f"Columns: {df.columns.tolist()}")
            s = io.StringIO()
            df.info(buf=s)
            # logging.info(f"df.info():\n{s.getvalue()}")
            logging.info(f"{'-' * 50}\n")
        return df


class DrugDateDifferenceTransformer(BaseEstimator, TransformerMixin):
    def __init__(
        self, drug_names: list[str], date_columns: list[str], verbose: bool = True
    ):
        self.drug_names = drug_names
        self.date_columns = date_columns
        self.verbose = verbose

        if self.verbose:
            logging.info(f"[{self.__class__.__name__}] Transformer initialized.")

    def fit(self, X: pd.DataFrame, y=None):
        return self

    def transform(self, X: pd.DataFrame, y=None):
        if self.verbose:
            logging.info(f"\n{'=' * 20} [{self.__class__.__name__}: Input] {'=' * 20}")
            logging.info(f"Shape: {X.shape}")
            logging.info(f"Columns: {X.columns.tolist()}")
            s = io.StringIO()
            X.info(buf=s)
            # logging.info(f"df.info():\n{s.getvalue()}")
            logging.info(f"{'=' * 50}\n")

        df = X.copy()

        # Compute date differences in days for each drug
        for drug in self.drug_names:
            start_col = f"{drug}_start_to_onset_days"
            stop_col = f"{drug}_stop_to_onset_days"
            start_stop_col = f"{drug}_start_stop_difference"

            df[start_col] = (
                df["date_of_onset_of_reaction"] - df[f"{drug}_start_date"]
            ).dt.days
            df[stop_col] = (
                df["date_of_onset_of_reaction"] - df[f"{drug}_stop_date"]
            ).dt.days
            df[start_stop_col] = (
                df[f"{drug}_stop_date"] - df[f"{drug}_start_date"]
            ).dt.days

        df = df.drop(columns=self.date_columns)

        if self.verbose:
            logging.info(f"\n{'-' * 20} [{self.__class__.__name__}: Output] {'-' * 20}")
            logging.info(f"Shape: {df.shape}")
            logging.info(f"Columns: {df.columns.tolist()}")
            s = io.StringIO()
            df.info(buf=s)
            # logging.info(f"df.info():\n{s.getvalue()}")
            logging.info(f"{'-' * 50}\n")

        return df


class NumberOfSuspectedDrugsTransformer(BaseEstimator, TransformerMixin):
    def __init__(self, drug_names: list[str], verbose: bool = True):
        self.drug_names = drug_names
        self.suspected_drugs_columns = [f"{drug}_suspected" for drug in drug_names]
        self.verbose = verbose

        if self.verbose:
            logging.info(f"[{self.__class__.__name__}] Transformer initialized.")

    def fit(self, X: pd.DataFrame, y=None):
        return self

    def transform(self, X: pd.DataFrame, y=None) -> pd.DataFrame:
        if self.verbose:
            logging.info(f"\n{'=' * 20} [{self.__class__.__name__}: Input] {'=' * 20}")
            logging.info(f"Shape: {X.shape}")
            logging.info(f"Columns: {X.columns.tolist()}")
            s = io.StringIO()
            X.info(buf=s)
            # logging.info(f"df.info():\n{s.getvalue()}")
            logging.info(f"{'=' * 50}\n")

        df = X.copy()

        # Make sure only existing columns are used
        cols = [col for col in self.suspected_drugs_columns if col in df.columns]

        if not cols:
            raise ValueError("No *_suspected columns found in DataFrame.")

        df["num_suspected_drugs"] = df[cols].sum(axis=1)

        if self.verbose:
            logging.info(f"\n{'-' * 20} [{self.__class__.__name__}: Output] {'-' * 20}")
            logging.info(f"Shape: {df.shape}")
            logging.info(f"Columns: {df.columns.tolist()}")
            s = io.StringIO()
            df.info(buf=s)
            # logging.info(f"df.info():\n{s.getvalue()}")
            logging.info(f"{'-' * 50}\n")

        return df


class DropColumnsTransformer(BaseEstimator, TransformerMixin):
    def __init__(self, columns: list[str], verbose: bool = True):
        self.columns = columns
        self.verbose = verbose

        if self.verbose:
            logging.info(f"[{self.__class__.__name__}] Transformer initialized.")

    def fit(self, X: pd.DataFrame, y=None):
        return self

    def transform(self, X: pd.DataFrame) -> pd.DataFrame:
        if self.verbose:
            logging.info(f"\n{'=' * 20} [{self.__class__.__name__}: Input] {'=' * 20}")
            logging.info(f"Shape: {X.shape}")
            logging.info(f"Columns: {X.columns.tolist()}")
            s = io.StringIO()
            X.info(buf=s)
            # logging.info(f"df.info():\n{s.getvalue()}")
            logging.info(f"{'=' * 50}\n")

        df = X.copy()

        existing_cols = [col for col in self.columns if col in df.columns]

        if self.verbose:
            logging.info(
                f"[{self.__class__.__name__}] Dropping columns: {existing_cols}"
            )

        df = df.drop(columns=existing_cols, errors="ignore")

        if self.verbose:
            logging.info(f"\n{'-' * 20} [{self.__class__.__name__}: Output] {'-' * 20}")
            logging.info(f"Shape: {df.shape}")
            logging.info(f"Columns: {df.columns.tolist()}")
            s = io.StringIO()
            df.info(buf=s)
            # logging.info(f"df.info():\n{s.getvalue()}")
            logging.info(f"{'-' * 50}\n")

        return df


class NumericalImputer(BaseEstimator, TransformerMixin):
    def __init__(self, numerical_columns: list[str], verbose: bool = True):
        self.numerical_columns = numerical_columns
        self.verbose = verbose

        if self.verbose:
            logging.info(f"[{self.__class__.__name__}] Transformer initialized.")

    def fit(self, X: pd.DataFrame, y=None):
        return self

    def transform(self, X: pd.DataFrame) -> pd.DataFrame:
        if self.verbose:
            logging.info(f"\n{'=' * 20} [{self.__class__.__name__}: Input] {'=' * 20}")
            logging.info(f"Shape: {X.shape}")
            logging.info(f"Columns: {X.columns.tolist()}")
            s = io.StringIO()
            X.info(buf=s)
            # logging.info(f"df.info():\n{s.getvalue()}")
            logging.info(f"{'=' * 50}\n")

        df = X.copy()
        for col in self.numerical_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")

        impute_cols = [col for col in self.numerical_columns if col in df.columns]
        df[impute_cols] = df[impute_cols].fillna(-1)

        if self.verbose:
            logging.info(f"\n{'-' * 20} [{self.__class__.__name__}: Output] {'-' * 20}")
            logging.info(f"Shape: {df.shape}")
            logging.info(f"Columns: {df.columns.tolist()}")
            s = io.StringIO()
            df.info(buf=s)
            # logging.info(f"df.info():\n{s.getvalue()}")
            logging.info(f"{'-' * 50}\n")

        return df


class PatientBMITransformer(BaseEstimator, TransformerMixin):
    def __init__(
        self,
        weight_col: str = "patient_weight_kg",
        height_col: str = "patient_height_cm",
        bmi_col: str = "patient_bmi",
        verbose: bool = True,
    ):
        self.weight_col = weight_col
        self.height_col = height_col
        self.bmi_col = bmi_col
        self.verbose = verbose
        if self.verbose:
            logging.info(f"[{self.__class__.__name__}] Transformer initialized.")

    def fit(self, X, y=None):
        return self

    def transform(self, X: pd.DataFrame) -> pd.DataFrame:
        if self.verbose:
            logging.info(f"\n{'=' * 20} [{self.__class__.__name__}: Input] {'=' * 20}")
            logging.info(f"Shape: {X.shape}")
            logging.info(f"Columns: {X.columns.tolist()}")
            s = io.StringIO()
            X.info(buf=s)
            # logging.info(f"df.info():\n{s.getvalue()}")
            logging.info(f"{'=' * 50}\n")

        df = X.copy()
        if self.weight_col not in X.columns or self.height_col not in X.columns:
            raise KeyError(
                f"Missing required columns: {self.weight_col}, {self.height_col}"
            )

        height_m = df[self.height_col] / 100
        df[self.bmi_col] = df[self.weight_col] / (height_m**2)

        if self.verbose:
            logging.info(f"\n{'-' * 20} [{self.__class__.__name__}: Output] {'-' * 20}")
            logging.info(f"Shape: {df.shape}")
            logging.info(f"Columns: {df.columns.tolist()}")
            s = io.StringIO()
            df.info(buf=s)
            # logging.info(f"df.info():\n{s.getvalue()}")
            logging.info(f"{'-' * 50}\n")

        return df


class FinalColumnSelectorTransformer(BaseEstimator, TransformerMixin):
    def __init__(self, columns: Union[str, List[str]], verbose: bool = True):
        if isinstance(columns, str):
            columns = [columns]
        self.columns = columns
        self.verbose = verbose

        if self.verbose:
            logging.info(f"[{self.__class__.__name__}] Transformer initialized.")

    def fit(self, X, y=None):
        return self

    def transform(self, X: pd.DataFrame) -> pd.DataFrame:
        if self.verbose:
            logging.info(f"\n{'=' * 20} [{self.__class__.__name__}: Input] {'=' * 20}")
            logging.info(f"Shape: {X.shape}")
            logging.info(f"Columns: {X.columns.tolist()}")
            s = io.StringIO()
            X.info(buf=s)
            # logging.info(f"df.info():\n{s.getvalue()}")
            logging.info(f"{'=' * 50}\n")

        X = X.copy()
        existing_cols = [col for col in self.columns if col in X.columns]
        missing_cols = [col for col in self.columns if col not in X.columns]

        if missing_cols:
            # Use logging.warning instead of print
            logging.warning(
                f"[{self.__class__.__name__}] Missing columns not found in DataFrame: {missing_cols}"
            )

        df_out = X[existing_cols]

        if self.verbose:
            logging.info(f"\n{'-' * 20} [{self.__class__.__name__}: Output] {'-' * 20}")
            logging.info(f"Shape: {df_out.shape}")
            logging.info(f"Columns: {df_out.columns.tolist()}")
            s = io.StringIO()
            df_out.info(buf=s)
            # logging.info(f"df.info():\n{s.getvalue()}")
            logging.info(f"{'-' * 50}\n")

        return df_out


class OneHotEncodingTransformer(BaseEstimator, TransformerMixin):
    def __init__(self, categorical_columns: list[str], verbose: bool = True):
        self.categorical_columns = categorical_columns
        self.encoder = OneHotEncoder(handle_unknown="ignore", sparse_output=False)
        self.feature_names_out = None
        self.verbose = verbose

        if self.verbose:
            logging.info(f"[{self.__class__.__name__}] Transformer initialized.")

    def fit(self, X: pd.DataFrame, y=None):
        # Fit encoder on categorical columns
        self.encoder.fit(X[self.categorical_columns])
        # Save output feature names
        self.feature_names_out = self.encoder.get_feature_names_out(
            self.categorical_columns
        )
        return self

    def transform(self, X: pd.DataFrame, y=None) -> pd.DataFrame:
        if self.verbose:
            logging.info(f"\n{'=' * 20} [{self.__class__.__name__}: Input] {'=' * 20}")
            logging.info(f"Shape: {X.shape}")
            logging.info(f"Columns: {X.columns.tolist()}")
            s = io.StringIO()
            X.info(buf=s)
            # logging.info(f"df.info():\n{s.getvalue()}")
            logging.info(f"{'=' * 50}\n")

        X_copy = X.copy()
        encoded = self.encoder.transform(X_copy[self.categorical_columns])
        encoded_df = pd.DataFrame(
            encoded, columns=self.feature_names_out, index=X_copy.index
        )
        X_copy = X_copy.drop(columns=self.categorical_columns)
        X_transformed = pd.concat([X_copy, encoded_df], axis=1)

        if self.verbose:
            logging.info(f"\n{'-' * 20} [{self.__class__.__name__}: Output] {'-' * 20}")
            logging.info(f"Shape: {X_transformed.shape}")
            logging.info(f"Columns: {X_transformed.columns.tolist()}")
            s = io.StringIO()
            X_transformed.info(buf=s)
            # logging.info(f"df.info():\n{s.getvalue()}")
            logging.info(f"{'-' * 50}\n")

        return X_transformed


class MinMaxScalingTransformer(BaseEstimator, TransformerMixin):
    def __init__(self, numerical_columns: list[str], verbose: bool = True):
        self.numerical_columns = numerical_columns
        self.scaler = MinMaxScaler()
        self.feature_names_out = numerical_columns
        self.verbose = verbose

        if self.verbose:
            logging.info(f"[{self.__class__.__name__}] Transformer initialized.")

    def fit(self, X: pd.DataFrame, y=None):
        self.scaler.fit(X[self.numerical_columns])
        return self

    def transform(self, X: pd.DataFrame, y=None) -> pd.DataFrame:
        if self.verbose:
            logging.info(f"\n{'=' * 20} [{self.__class__.__name__}: Input] {'=' * 20}")
            logging.info(f"Shape: {X.shape}")
            logging.info(f"Columns: {X.columns.tolist()}")
            s = io.StringIO()
            X.info(buf=s)
            # logging.info(f"df.info():\n{s.getvalue()}")
            logging.info(f"{'=' * 50}\n")

        X_copy = X.copy()
        scaled_values = self.scaler.transform(X_copy[self.numerical_columns])
        scaled_df = pd.DataFrame(
            scaled_values, columns=self.feature_names_out, index=X_copy.index
        )
        X_copy[self.numerical_columns] = scaled_df

        if self.verbose:
            logging.info(f"\n{'-' * 20} [{self.__class__.__name__}: Output] {'-' * 20}")
            logging.info(f"Shape: {X_copy.shape}")
            logging.info(f"Columns: {X_copy.columns.tolist()}")
            s = io.StringIO()
            X_copy.info(buf=s)
            # logging.info(f"df.info():\n{s.getvalue()}")
            logging.info(f"{'-' * 50}\n")

        return X_copy
