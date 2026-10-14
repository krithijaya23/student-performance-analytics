"""
visualizations.py
-----------------
Reusable Plotly chart builders for the dashboard pages.
All functions return a Plotly figure object.
"""

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ── Brand palette ──────────────────────────────────────────────────────────────
NAVY    = "#1B2A4A"
BLUE    = "#2563EB"
TEAL    = "#0D9488"
LIGHT   = "#F0F4FF"
GREY    = "#94A3B8"
WHITE   = "#FFFFFF"
ACCENT  = "#F59E0B"

CHART_TEMPLATE = "plotly_white"


def grade_distribution(df: pd.DataFrame, subject: str) -> go.Figure:
    """Histogram of G3 final grades."""
    fig = px.histogram(
        df, x="G3", nbins=21,
        title=f"Final Grade Distribution — {subject}",
        labels={"G3": "Final Grade (G3)", "count": "Number of Students"},
        color_discrete_sequence=[BLUE],
        template=CHART_TEMPLATE,
    )
    fig.update_traces(marker_line_width=1, marker_line_color=WHITE)
    fig.update_layout(
        title_font_size=16,
        xaxis=dict(dtick=1),
        bargap=0.05,
        plot_bgcolor=WHITE,
    )
    return fig


def subject_grade_comparison(mat_df: pd.DataFrame | None,
                              por_df: pd.DataFrame | None) -> go.Figure:
    """Box plot comparing G3 distributions across subjects."""
    frames = []
    if mat_df is not None:
        frames.append(mat_df[["G3"]].assign(Subject="Mathematics"))
    if por_df is not None:
        frames.append(por_df[["G3"]].assign(Subject="Portuguese"))

    if not frames:
        fig = go.Figure()
        fig.add_annotation(text="No data available", showarrow=False)
        return fig

    combined = pd.concat(frames, ignore_index=True)
    fig = px.box(
        combined, x="Subject", y="G3",
        color="Subject",
        title="Grade Distribution by Subject",
        labels={"G3": "Final Grade (G3)"},
        color_discrete_map={"Mathematics": BLUE, "Portuguese": TEAL},
        template=CHART_TEMPLATE,
    )
    fig.update_layout(title_font_size=16, showlegend=False)
    return fig


def correlation_heatmap(df: pd.DataFrame, title: str = "Feature Correlation") -> go.Figure:
    """Heatmap of numeric feature correlations (excluding G1, G2)."""
    num_cols = df.select_dtypes(include="number").columns.tolist()
    drop = [c for c in ["G1", "G2"] if c in num_cols]
    num_cols = [c for c in num_cols if c not in drop]

    corr = df[num_cols].corr()

    fig = go.Figure(data=go.Heatmap(
        z=corr.values,
        x=corr.columns.tolist(),
        y=corr.index.tolist(),
        colorscale="RdBu",
        zmid=0,
        text=np.round(corr.values, 2),
        texttemplate="%{text}",
        textfont={"size": 9},
        colorbar=dict(title="r"),
    ))
    fig.update_layout(
        title=title,
        title_font_size=16,
        template=CHART_TEMPLATE,
        height=520,
        xaxis=dict(tickangle=-45),
    )
    return fig


def model_metrics_bar(metrics_df: pd.DataFrame) -> go.Figure:
    """Grouped bar chart of MAE, RMSE, R² by model."""
    trained = metrics_df[metrics_df["Status"] == "Trained"].copy()
    if trained.empty:
        fig = go.Figure()
        fig.add_annotation(text="No trained models to display", showarrow=False)
        return fig

    fig = go.Figure()
    for metric, colour in [("MAE", BLUE), ("RMSE", TEAL), ("R²", ACCENT)]:
        fig.add_trace(go.Bar(
            name=metric,
            x=trained["Model"],
            y=trained[metric].astype(float),
            marker_color=colour,
        ))

    fig.update_layout(
        barmode="group",
        title="Model Comparison — Test-Set Metrics",
        title_font_size=16,
        xaxis_title="Model",
        yaxis_title="Score",
        template=CHART_TEMPLATE,
        legend_title="Metric",
    )
    return fig


def actual_vs_predicted(y_test, y_pred, model_name: str) -> go.Figure:
    """Scatter plot: actual vs predicted grades."""
    perfect = [0, 20]
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=y_test, y=y_pred,
        mode="markers",
        marker=dict(color=BLUE, opacity=0.6, size=7),
        name="Students",
    ))
    fig.add_trace(go.Scatter(
        x=perfect, y=perfect,
        mode="lines",
        line=dict(color=GREY, dash="dash"),
        name="Perfect Prediction",
    ))
    fig.update_layout(
        title=f"Actual vs Predicted — {model_name}",
        title_font_size=16,
        xaxis_title="Actual G3",
        yaxis_title="Predicted G3",
        template=CHART_TEMPLATE,
    )
    return fig


def residual_plot(y_test, y_pred, model_name: str) -> go.Figure:
    """Residual plot (predicted - actual)."""
    residuals = np.array(y_pred) - np.array(y_test)
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=y_pred, y=residuals,
        mode="markers",
        marker=dict(color=TEAL, opacity=0.6, size=7),
        name="Residual",
    ))
    fig.add_hline(y=0, line_dash="dash", line_color=GREY)
    fig.update_layout(
        title=f"Residual Plot — {model_name}",
        title_font_size=16,
        xaxis_title="Predicted G3",
        yaxis_title="Residual (Predicted − Actual)",
        template=CHART_TEMPLATE,
    )
    return fig


def feature_importance(pipeline, feature_names: list[str],
                        model_name: str, top_n: int = 15) -> go.Figure:
    """
    Horizontal bar chart of feature importances for tree-based models.
    Falls back gracefully if importances are not available.
    """
    model = pipeline.named_steps["model"]
    if not hasattr(model, "feature_importances_"):
        fig = go.Figure()
        fig.add_annotation(
            text=f"{model_name} does not support feature importances.",
            showarrow=False, font=dict(size=13),
        )
        return fig

    importances = model.feature_importances_

    # Get transformed feature names from the ColumnTransformer
    preprocessor = pipeline.named_steps["preprocessor"]
    try:
        tf_names = preprocessor.get_feature_names_out()
    except Exception:
        tf_names = [f"feature_{i}" for i in range(len(importances))]

    # Tidy names: remove "num__" / "cat__" prefixes
    clean_names = [n.split("__")[-1] for n in tf_names]

    imp_df = (
        pd.DataFrame({"Feature": clean_names, "Importance": importances})
        .sort_values("Importance", ascending=False)
        .head(top_n)
        .sort_values("Importance")
    )

    fig = px.bar(
        imp_df, x="Importance", y="Feature",
        orientation="h",
        title=f"Top {top_n} Feature Importances — {model_name}",
        color="Importance",
        color_continuous_scale=[[0, LIGHT], [1, NAVY]],
        template=CHART_TEMPLATE,
    )
    fig.update_layout(
        title_font_size=16,
        coloraxis_showscale=False,
        yaxis_title="",
    )
    return fig


def studytime_vs_grade(df: pd.DataFrame, subject: str) -> go.Figure:
    """Box plot of G3 by weekly study time."""
    labels = {1: "< 2 hrs", 2: "2–5 hrs", 3: "5–10 hrs", 4: "> 10 hrs"}
    plot_df = df[["studytime", "G3"]].copy()
    plot_df["Study Time"] = plot_df["studytime"].map(labels).fillna("Unknown")
    order = list(labels.values())

    fig = px.box(
        plot_df, x="Study Time", y="G3",
        category_orders={"Study Time": order},
        title=f"Study Time vs Final Grade — {subject}",
        labels={"G3": "Final Grade (G3)"},
        color="Study Time",
        color_discrete_sequence=px.colors.sequential.Blues_r,
        template=CHART_TEMPLATE,
    )
    fig.update_layout(title_font_size=16, showlegend=False)
    return fig


def absences_vs_grade(df: pd.DataFrame, subject: str) -> go.Figure:
    """Scatter plot of absences vs G3 with a trend line."""
    fig = px.scatter(
        df, x="absences", y="G3",
        trendline="ols",
        title=f"Absences vs Final Grade — {subject}",
        labels={"absences": "Number of Absences", "G3": "Final Grade (G3)"},
        color_discrete_sequence=[TEAL],
        template=CHART_TEMPLATE,
        opacity=0.65,
    )
    fig.update_layout(title_font_size=16)
    return fig


def categorical_grade_breakdown(df: pd.DataFrame, col: str,
                                 subject: str) -> go.Figure:
    """Box plot of G3 grouped by a categorical column."""
    fig = px.box(
        df, x=col, y="G3",
        title=f"Grade by {col} — {subject}",
        labels={"G3": "Final Grade (G3)", col: col},
        color=col,
        template=CHART_TEMPLATE,
    )
    fig.update_layout(title_font_size=16, showlegend=False)
    return fig
