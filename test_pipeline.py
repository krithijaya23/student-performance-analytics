"""
test_pipeline.py
----------------
Functional test: load data, preprocess, train models, predict, verify metrics.
Run with: python test_pipeline.py
"""

import sys, os
sys.path.insert(0, os.path.dirname(__file__))

import traceback
import numpy as np
import pandas as pd

PASS = "✅ PASS"
FAIL = "❌ FAIL"
WARN = "⚠️  WARN"

results = []

def check(name, fn):
    try:
        result = fn()
        status = PASS if result is not False else FAIL
        msg = ""
        if isinstance(result, str):
            msg = result
        results.append((status, name, msg))
        print(f"{status}  {name}  {msg}")
        return result
    except Exception as e:
        results.append((FAIL, name, str(e)))
        print(f"{FAIL}  {name}  {e}")
        traceback.print_exc()
        return None

print("\n" + "="*60)
print(" Student Performance Analytics — Functional Test")
print("="*60 + "\n")

# ── 1. Imports ────────────────────────────────────────────────────────────────
check("Import data_loader",      lambda: __import__("src.data_loader",      fromlist=[""]))
check("Import preprocessing",    lambda: __import__("src.preprocessing",    fromlist=[""]))
check("Import train_models",     lambda: __import__("src.train_models",     fromlist=[""]))
check("Import evaluation",       lambda: __import__("src.evaluation",       fromlist=[""]))
check("Import predictions",      lambda: __import__("src.predictions",      fromlist=[""]))
check("Import visualizations",   lambda: __import__("src.visualizations",   fromlist=[""]))

# ── 2. Dataset loading ────────────────────────────────────────────────────────
from src.data_loader import load_uci_dataset, get_feature_columns, get_all_feature_columns

mat_df = None
por_df = None

def load_math():
    global mat_df
    df, status = load_uci_dataset("Mathematics")
    if df is None:
        return f"NOT LOADED — {status}"
    mat_df = df
    return f"{len(df)} rows, {len(df.columns)} columns"

def load_por():
    global por_df
    df, status = load_uci_dataset("Portuguese")
    if df is None:
        return f"NOT LOADED — {status}"
    por_df = df
    return f"{len(df)} rows, {len(df.columns)} columns"

check("Load Mathematics dataset",  load_math)
check("Load Portuguese dataset",   load_por)

# ── 3. Schema checks ──────────────────────────────────────────────────────────
def check_target(df, name):
    if df is None:
        return f"Skipped (dataset not loaded)"
    assert "G3" in df.columns, "G3 column missing"
    assert "G1" in df.columns, "G1 column missing"
    assert "G2" in df.columns, "G2 column missing"
    return f"G3 range: {df['G3'].min()}–{df['G3'].max()}, mean: {df['G3'].mean():.2f}"

check("Math — target G3 present",  lambda: check_target(mat_df, "Math"))
check("Por  — target G3 present",  lambda: check_target(por_df, "Por"))

def check_no_g1g2_in_features(df):
    if df is None:
        return "Skipped"
    num, cat = get_feature_columns(df)
    all_f = num + cat
    assert "G1" not in all_f, "G1 found in input features!"
    assert "G2" not in all_f, "G2 found in input features!"
    assert "G3" not in all_f, "G3 found in input features!"
    return f"{len(all_f)} features ({len(num)} numerical, {len(cat)} categorical)"

check("Math — G1/G2/G3 excluded from features", lambda: check_no_g1g2_in_features(mat_df))
check("Por  — G1/G2/G3 excluded from features", lambda: check_no_g1g2_in_features(por_df))

# ── 4. Preprocessing ──────────────────────────────────────────────────────────
from src.preprocessing import build_preprocessor, prepare_data

def test_preprocessor(df, name):
    if df is None:
        return "Skipped"
    X, y = prepare_data(df)
    preprocessor = build_preprocessor(df)
    from sklearn.model_selection import train_test_split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    preprocessor.fit(X_train)
    X_tr = preprocessor.transform(X_train)
    X_te = preprocessor.transform(X_test)
    assert X_tr.shape[0] == len(X_train)
    assert X_te.shape[0] == len(X_test)
    assert X_tr.shape[1] == X_te.shape[1]
    return f"Transformed shapes: train {X_tr.shape}, test {X_te.shape}"

check("Math — preprocessing pipeline", lambda: test_preprocessor(mat_df, "Math"))
check("Por  — preprocessing pipeline", lambda: test_preprocessor(por_df, "Por"))

# ── 5. Model training ─────────────────────────────────────────────────────────
from src.train_models import train_all_models, get_best_model, build_metrics_table

math_results = None
por_results  = None

def train_math():
    global math_results
    if mat_df is None:
        return "Skipped"
    res, _, _ = train_all_models(mat_df, "math")
    math_results = res
    trained = sum(1 for v in res.values() if v["status"] == "trained")
    return f"{trained}/4 models trained"

def train_por():
    global por_results
    if por_df is None:
        return "Skipped"
    res, _, _ = train_all_models(por_df, "por")
    por_results = res
    trained = sum(1 for v in res.values() if v["status"] == "trained")
    return f"{trained}/4 models trained"

check("Train all models — Mathematics", train_math)
check("Train all models — Portuguese",  train_por)

# ── 6. Metrics ────────────────────────────────────────────────────────────────
def check_metrics(results, name):
    if results is None:
        return "Skipped"
    rows = []
    for model_name, info in results.items():
        if info["status"] == "trained":
            m = info["test_metrics"]
            assert 0 <= m["MAE"] <= 20, f"MAE out of range: {m['MAE']}"
            assert 0 <= m["RMSE"] <= 20, f"RMSE out of range: {m['RMSE']}"
            assert -10 <= m["R2"] <= 1.01, f"R² out of range: {m['R2']}"
            rows.append(f"{model_name}: MAE={m['MAE']}, RMSE={m['RMSE']}, R²={m['R2']}")
    return " | ".join(rows)

check("Math — metrics valid", lambda: check_metrics(math_results, "Math"))
check("Por  — metrics valid", lambda: check_metrics(por_results,  "Por"))

# ── 7. Best model selection ───────────────────────────────────────────────────
def check_best(results, name):
    if results is None:
        return "Skipped"
    best = get_best_model(results)
    assert best is not None, "No best model found"
    m = results[best]["test_metrics"]
    return f"Best: {best} (RMSE={m['RMSE']})"

check("Math — best model selection", lambda: check_best(math_results, "Math"))
check("Por  — best model selection", lambda: check_best(por_results,  "Por"))

# ── 8. Prediction ─────────────────────────────────────────────────────────────
from src.predictions import predict_grade

def test_prediction(df, results, name):
    if df is None or results is None:
        return "Skipped"
    best = get_best_model(results)
    if best is None:
        return "No trained model"
    pipeline = results[best]["pipeline"]

    # Build a sample input from the first row
    num_cols, cat_cols = get_feature_columns(df)
    sample_row = df[num_cols + cat_cols].iloc[0].to_dict()

    pred = predict_grade(pipeline, sample_row)
    assert 0 <= pred <= 20, f"Prediction out of range: {pred}"
    return f"Predicted G3={pred:.2f} using {best}"

check("Math — single prediction", lambda: test_prediction(mat_df, math_results, "Math"))
check("Por  — single prediction", lambda: test_prediction(por_df,  por_results,  "Por"))

# ── 9. Missing value handling ─────────────────────────────────────────────────
def test_missing_values(df, results, name):
    if df is None or results is None:
        return "Skipped"
    best = get_best_model(results)
    if best is None:
        return "No trained model"
    pipeline = results[best]["pipeline"]

    num_cols, cat_cols = get_feature_columns(df)
    sample_row = df[num_cols + cat_cols].iloc[0].to_dict()

    # Introduce NaN values
    import math
    for k in list(sample_row.keys())[:3]:
        sample_row[k] = None

    pred = predict_grade(pipeline, sample_row)
    assert 0 <= pred <= 20
    return f"Prediction with NaN inputs: G3={pred:.2f}"

check("Math — handles NaN inputs", lambda: test_missing_values(mat_df, math_results, "Math"))
check("Por  — handles NaN inputs", lambda: test_missing_values(por_df,  por_results,  "Por"))

# ── 10. Metrics table ─────────────────────────────────────────────────────────
def test_metrics_table(results, name):
    if results is None:
        return "Skipped"
    tbl = build_metrics_table(results)
    assert isinstance(tbl, pd.DataFrame)
    assert "Model" in tbl.columns
    return f"{len(tbl)} rows in metrics table"

check("Math — metrics table", lambda: test_metrics_table(math_results, "Math"))
check("Por  — metrics table", lambda: test_metrics_table(por_results,  "Por"))

# ── Summary ───────────────────────────────────────────────────────────────────
print("\n" + "="*60)
n_pass = sum(1 for s, _, _ in results if s == PASS)
n_fail = sum(1 for s, _, _ in results if s == FAIL)
print(f" Results: {n_pass} passed, {n_fail} failed out of {len(results)} tests")
print("="*60)

# ── Print actual metrics for the report ──────────────────────────────────────
print("\n📊 ACTUAL MODEL METRICS (copy these into PROJECT_REPORT.md)\n")
for subject, res in [("Mathematics", math_results), ("Portuguese", por_results)]:
    if res is None:
        print(f"{subject}: dataset not loaded\n")
        continue
    print(f"--- {subject} ---")
    for model_name, info in res.items():
        if info["status"] == "trained":
            m = info["test_metrics"]
            print(f"  {model_name:25s}  MAE={m['MAE']:.4f}  RMSE={m['RMSE']:.4f}  R²={m['R2']:.4f}")
        else:
            print(f"  {model_name:25s}  FAILED: {info['error']}")
    best = get_best_model(res)
    print(f"  Best model: {best}\n")

if n_fail > 0:
    sys.exit(1)
