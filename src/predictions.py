"""
predictions.py
--------------
Runs predictions using a trained pipeline.
Validates that input columns match the pipeline's expected schema.
"""

import pandas as pd
import numpy as np
from sklearn.pipeline import Pipeline


def predict_grade(pipeline: Pipeline, input_dict: dict) -> float:
    """
    Predict the final grade (G3) for a single student.

    Parameters
    ----------
    pipeline : trained sklearn Pipeline (preprocessor + model)
    input_dict : dict of {feature_name: value}

    Returns
    -------
    Predicted grade as a float, clipped to [0, 20].
    """
    input_df = pd.DataFrame([input_dict])
    raw_pred = pipeline.predict(input_df)[0]
    return float(np.clip(raw_pred, 0, 20))


def get_expected_features(pipeline: Pipeline) -> list[str]:
    """
    Extract the list of feature names the pipeline expects.
    Works by inspecting the ColumnTransformer inside the pipeline.
    """
    preprocessor = pipeline.named_steps["preprocessor"]
    feature_names = []
    for _, _, cols in preprocessor.transformers_:
        if isinstance(cols, list):
            feature_names.extend(cols)
    return feature_names
