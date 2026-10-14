"""
train_models.py
---------------
Trains and evaluates multiple regression models on a prepared dataset.
Uses an 80/20 train-test split with random_state=42 for reproducibility.
"""

import os
import time
import joblib
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LinearRegression
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

from src.preprocessing import build_preprocessor, prepare_data

MODELS_DIR = os.path.join(os.path.dirname(__file__), "..", "models")

RANDOM_STATE = 42
TEST_SIZE = 0.20

MODEL_DEFINITIONS = {
    "Linear Regression": LinearRegression(),
    "Decision Tree": DecisionTreeRegressor(random_state=RANDOM_STATE),
    "Random Forest": RandomForestRegressor(n_estimators=100, random_state=RANDOM_STATE),
    "Gradient Boosting": GradientBoostingRegressor(n_estimators=100, random_state=RANDOM_STATE),
}


def _compute_metrics(y_true, y_pred) -> dict:
    """Calculate MAE, RMSE, and R²."""
    mae = mean_absolute_error(y_true, y_pred)
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    r2 = r2_score(y_true, y_pred)
    return {"MAE": round(mae, 4), "RMSE": round(rmse, 4), "R2": round(r2, 4)}


def train_all_models(df: pd.DataFrame, dataset_label: str) -> dict:
    """
    Train all models on the provided DataFrame.

    Parameters
    ----------
    df : DataFrame — raw dataset including target column G3
    dataset_label : str — short label used for saving model files (e.g. "math")

    Returns
    -------
    results : dict keyed by model name, each value is:
        {
          "pipeline": fitted Pipeline,
          "train_metrics": {...},
          "test_metrics": {...},
          "y_test": array,
          "y_pred": array,
          "status": "trained" | "failed",
          "error": str or None,
          "train_time_s": float,
        }
    """
    X, y = prepare_data(df)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=TEST_SIZE, random_state=RANDOM_STATE
    )

    preprocessor = build_preprocessor(df)
    results = {}

    for model_name, estimator in MODEL_DEFINITIONS.items():
        try:
            pipeline = Pipeline([
                ("preprocessor", preprocessor),
                ("model", estimator),
            ])

            t0 = time.time()
            pipeline.fit(X_train, y_train)
            elapsed = round(time.time() - t0, 2)

            y_pred_train = pipeline.predict(X_train)
            y_pred_test = pipeline.predict(X_test)

            results[model_name] = {
                "pipeline": pipeline,
                "train_metrics": _compute_metrics(y_train, y_pred_train),
                "test_metrics": _compute_metrics(y_test, y_pred_test),
                "y_test": y_test.values,
                "y_pred": y_pred_test,
                "X_test": X_test,
                "status": "trained",
                "error": None,
                "train_time_s": elapsed,
            }

            # Persist pipeline to disk
            os.makedirs(MODELS_DIR, exist_ok=True)
            safe_name = model_name.lower().replace(" ", "_")
            save_path = os.path.join(MODELS_DIR, f"{dataset_label}_{safe_name}.pkl")
            joblib.dump(pipeline, save_path)

        except Exception as e:
            results[model_name] = {
                "pipeline": None,
                "train_metrics": None,
                "test_metrics": None,
                "y_test": None,
                "y_pred": None,
                "X_test": None,
                "status": "failed",
                "error": str(e),
                "train_time_s": None,
            }

    return results, X_test, y_test


def get_best_model(results: dict) -> str | None:
    """
    Return the model name with the lowest test-set RMSE.
    Only considers models with status == 'trained'.
    """
    best_name = None
    best_rmse = float("inf")

    for name, info in results.items():
        if info["status"] == "trained" and info["test_metrics"]:
            rmse = info["test_metrics"]["RMSE"]
            if rmse < best_rmse:
                best_rmse = rmse
                best_name = name

    return best_name


def build_metrics_table(results: dict) -> pd.DataFrame:
    """Return a tidy DataFrame of per-model test-set metrics."""
    rows = []
    for name, info in results.items():
        if info["status"] == "trained" and info["test_metrics"]:
            m = info["test_metrics"]
            rows.append({
                "Model": name,
                "MAE": m["MAE"],
                "RMSE": m["RMSE"],
                "R²": m["R2"],
                "Train Time (s)": info["train_time_s"],
                "Status": "Trained",
            })
        else:
            rows.append({
                "Model": name,
                "MAE": "—",
                "RMSE": "—",
                "R²": "—",
                "Train Time (s)": "—",
                "Status": f"Failed: {info['error']}",
            })
    return pd.DataFrame(rows)
