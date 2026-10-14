"""
preprocessing.py
----------------
Builds scikit-learn preprocessing pipelines for the UCI student dataset.
Handles numeric imputation + scaling and categorical one-hot encoding.
"""

import pandas as pd
import numpy as np
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.impute import SimpleImputer

from src.data_loader import get_feature_columns, TARGET_COL, EXCLUDE_COLS


def build_preprocessor(df: pd.DataFrame) -> ColumnTransformer:
    """
    Create a ColumnTransformer that:
    - Imputes missing numeric values with the median, then scales them
    - Imputes missing categorical values with 'missing', then one-hot encodes

    Parameters
    ----------
    df : DataFrame
        The raw dataset (used to detect column names only)

    Returns
    -------
    ColumnTransformer
    """
    num_cols, cat_cols = get_feature_columns(df)

    numeric_pipeline = Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler()),
    ])

    categorical_pipeline = Pipeline([
        ("imputer", SimpleImputer(strategy="constant", fill_value="missing")),
        ("encoder", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
    ])

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", numeric_pipeline, num_cols),
            ("cat", categorical_pipeline, cat_cols),
        ],
        remainder="drop",   # drop G1, G2, and any other unlisted columns
    )

    return preprocessor


def prepare_data(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series]:
    """
    Split DataFrame into X (features) and y (target G3).
    Drops G1, G2, G3 from X to prevent data leakage.

    Returns
    -------
    X : DataFrame of input features
    y : Series of G3 values
    """
    num_cols, cat_cols = get_feature_columns(df)
    feature_cols = num_cols + cat_cols

    X = df[feature_cols].copy()
    y = df[TARGET_COL].copy()

    return X, y
