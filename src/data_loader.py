"""
data_loader.py
--------------
Handles downloading and loading of student performance datasets.
Supports the UCI Student Performance dataset (Math + Portuguese).
"""

import os
import io
import zipfile
import requests
import pandas as pd
import streamlit as st

# ── Directory where CSV files are stored ──────────────────────────────────────
DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")

# ── UCI dataset metadata ───────────────────────────────────────────────────────
UCI_DOWNLOAD_URL = "https://archive.ics.uci.edu/static/public/320/student+performance.zip"

UCI_DATASETS = {
    "Mathematics": {
        "filename": "student-mat.csv",
        "subject": "Mathematics",
        "records": 395,
        "source": "UCI Machine Learning Repository",
        "url": "https://archive.ics.uci.edu/dataset/320/student+performance",
        "license": "CC BY 4.0",
        "target": "G3",
        "description": (
            "Mathematics student records from two Portuguese secondary schools "
            "(Gabriel Pereira and Mousinho da Silveira). Contains demographic, "
            "social, and academic features collected via school reports and questionnaires."
        ),
    },
    "Portuguese": {
        "filename": "student-por.csv",
        "subject": "Portuguese Language",
        "records": 649,
        "source": "UCI Machine Learning Repository",
        "url": "https://archive.ics.uci.edu/dataset/320/student+performance",
        "license": "CC BY 4.0",
        "target": "G3",
        "description": (
            "Portuguese language student records from the same two schools as the "
            "Mathematics dataset. Part of the same study by Cortez & Silva (2008)."
        ),
    },
}

# ── Column definitions ─────────────────────────────────────────────────────────
# G1 and G2 are first/second period grades — excluded from default features
# to avoid using intermediate grades when estimating the final grade.
EXCLUDE_COLS = ["G1", "G2", "G3"]

CATEGORICAL_COLS = [
    "school", "sex", "address", "famsize", "Pstatus",
    "Mjob", "Fjob", "reason", "guardian",
    "schoolsup", "famsup", "paid", "activities",
    "nursery", "higher", "internet", "romantic",
]

NUMERICAL_COLS = [
    "age", "Medu", "Fedu", "traveltime", "studytime",
    "failures", "famrel", "freetime", "goout",
    "Dalc", "Walc", "health", "absences",
]

TARGET_COL = "G3"

# Human-readable labels for prediction form
FEATURE_LABELS = {
    "school":     "School (GP = Gabriel Pereira, MS = Mousinho da Silveira)",
    "sex":        "Sex",
    "age":        "Age (years)",
    "address":    "Home address type",
    "famsize":    "Family size",
    "Pstatus":    "Parents' cohabitation status",
    "Medu":       "Mother's education level (0–4)",
    "Fedu":       "Father's education level (0–4)",
    "Mjob":       "Mother's job",
    "Fjob":       "Father's job",
    "reason":     "Reason for choosing this school",
    "guardian":   "Student's guardian",
    "traveltime": "Home–school travel time (1=<15min … 4=>1hr)",
    "studytime":  "Weekly study time (1=<2hrs … 4=>10hrs)",
    "failures":   "Number of past class failures (0–4)",
    "schoolsup":  "Extra educational support from school",
    "famsup":     "Family educational support",
    "paid":       "Extra paid classes within the course subject",
    "activities": "Extracurricular activities",
    "nursery":    "Attended nursery school",
    "higher":     "Wants to pursue higher education",
    "internet":   "Internet access at home",
    "romantic":   "In a romantic relationship",
    "famrel":     "Quality of family relationships (1=very bad … 5=excellent)",
    "freetime":   "Free time after school (1=very low … 5=very high)",
    "goout":      "Going out with friends (1=very low … 5=very high)",
    "Dalc":       "Workday alcohol consumption (1=very low … 5=very high)",
    "Walc":       "Weekend alcohol consumption (1=very low … 5=very high)",
    "health":     "Current health status (1=very bad … 5=very good)",
    "absences":   "Number of school absences",
}


def _csv_path(filename: str) -> str:
    """Return the full path to a CSV file in the data directory."""
    return os.path.join(DATA_DIR, filename)


def _try_download_uci() -> bool:
    """
    Attempt to download and extract the UCI Student Performance ZIP.
    Returns True if successful, False otherwise.
    """
    mat_path = _csv_path("student-mat.csv")
    por_path = _csv_path("student-por.csv")

    # Already present
    if os.path.exists(mat_path) and os.path.exists(por_path):
        return True

    try:
        response = requests.get(UCI_DOWNLOAD_URL, timeout=30)
        response.raise_for_status()

        # The outer ZIP contains another ZIP called student.zip
        outer_zip = zipfile.ZipFile(io.BytesIO(response.content))

        # Find the inner student.zip
        inner_zip_name = None
        for name in outer_zip.namelist():
            if name.endswith("student.zip"):
                inner_zip_name = name
                break

        if inner_zip_name:
            inner_bytes = outer_zip.read(inner_zip_name)
            inner_zip = zipfile.ZipFile(io.BytesIO(inner_bytes))
            for fname in ["student-mat.csv", "student-por.csv"]:
                for entry in inner_zip.namelist():
                    if entry.endswith(fname):
                        data = inner_zip.read(entry)
                        with open(_csv_path(fname), "wb") as f:
                            f.write(data)
        else:
            # Try flat extraction
            for fname in ["student-mat.csv", "student-por.csv"]:
                for entry in outer_zip.namelist():
                    if entry.endswith(fname):
                        data = outer_zip.read(entry)
                        with open(_csv_path(fname), "wb") as f:
                            f.write(data)

        return os.path.exists(mat_path) and os.path.exists(por_path)

    except Exception:
        return False


@st.cache_data(show_spinner=False)
def load_uci_dataset(subject: str) -> tuple[pd.DataFrame | None, str]:
    """
    Load a UCI Student Performance CSV.

    Parameters
    ----------
    subject : str
        Either "Mathematics" or "Portuguese"

    Returns
    -------
    (DataFrame or None, status_message)
    """
    meta = UCI_DATASETS[subject]
    filepath = _csv_path(meta["filename"])

    # Try automatic download if file is missing
    if not os.path.exists(filepath):
        _try_download_uci()

    if not os.path.exists(filepath):
        msg = (
            f"**{meta['filename']} not found.**\n\n"
            "Please download manually:\n"
            "1. Visit https://archive.ics.uci.edu/dataset/320/student+performance\n"
            "2. Download and extract the ZIP\n"
            "3. Place `student-mat.csv` and `student-por.csv` in the `data/` folder"
        )
        return None, msg

    try:
        df = pd.read_csv(filepath, sep=";")

        # Basic validation
        if TARGET_COL not in df.columns:
            return None, f"Column '{TARGET_COL}' not found. Check the CSV format."

        if len(df) < 10:
            return None, f"Dataset has too few rows ({len(df)}). File may be corrupt."

        return df, "ok"

    except Exception as e:
        return None, f"Failed to read {meta['filename']}: {e}"


def get_feature_columns(df: pd.DataFrame) -> tuple[list[str], list[str]]:
    """
    Return (numerical_features, categorical_features) excluding G1, G2, G3.
    Only includes columns that actually exist in the DataFrame.
    """
    num_cols = [c for c in NUMERICAL_COLS if c in df.columns]
    cat_cols = [c for c in CATEGORICAL_COLS if c in df.columns]
    return num_cols, cat_cols


def get_all_feature_columns(df: pd.DataFrame) -> list[str]:
    """Return all input feature column names (no G1, G2, G3)."""
    num, cat = get_feature_columns(df)
    return num + cat
