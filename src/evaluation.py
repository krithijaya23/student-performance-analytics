"""
evaluation.py
-------------
Metric explanations and helper functions for the model evaluation page.
"""

import numpy as np
import pandas as pd


METRIC_EXPLANATIONS = {
    "MAE": (
        "**Mean Absolute Error (MAE)** — The average difference between the predicted "
        "grade and the actual grade, measured in grade points. "
        "Lower is better. An MAE of 2.0 means predictions are off by about 2 points on average."
    ),
    "RMSE": (
        "**Root Mean Squared Error (RMSE)** — Similar to MAE but penalises large errors more "
        "heavily. Lower is better. RMSE is the primary model selection criterion here."
    ),
    "R2": (
        "**R² (R-squared)** — The proportion of variance in the final grade that the model "
        "explains. Ranges from 0 to 1; higher is better. An R² of 0.50 means the model "
        "explains 50% of the variation in grades."
    ),
}


def grade_band(grade: float) -> str:
    """Convert a numeric grade (0–20) to a descriptive band."""
    if grade >= 16:
        return "Excellent (16–20)"
    elif grade >= 14:
        return "Good (14–15)"
    elif grade >= 10:
        return "Sufficient (10–13)"
    else:
        return "Insufficient (0–9)"


def interpretation(predicted: float) -> str:
    """Return a friendly interpretation of a predicted grade."""
    band = grade_band(predicted)
    if predicted >= 16:
        return (
            f"Estimated grade: **{predicted:.1f} / 20** — {band}. "
            "The student profile suggests strong academic performance."
        )
    elif predicted >= 14:
        return (
            f"Estimated grade: **{predicted:.1f} / 20** — {band}. "
            "The student profile suggests above-average performance."
        )
    elif predicted >= 10:
        return (
            f"Estimated grade: **{predicted:.1f} / 20** — {band}. "
            "The student profile suggests adequate performance, with room for improvement."
        )
    else:
        return (
            f"Estimated grade: **{predicted:.1f} / 20** — {band}. "
            "The student profile suggests the student may face challenges. "
            "Additional support could be beneficial."
        )
