"""
4_Model_Comparison.py  —  Model Comparison
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from src.data_loader   import load_uci_dataset, get_all_feature_columns
from src.train_models  import train_all_models, get_best_model, build_metrics_table
from src.evaluation    import METRIC_EXPLANATIONS
from src.styles        import inject_css, sidebar_nav, page_header, kpi_card
from src.visualizations import (
    actual_vs_predicted, residual_plot, feature_importance, CHART_TEMPLATE
)

st.set_page_config(page_title="Model Comparison", page_icon="📊", layout="wide")
inject_css()
sidebar_nav()

page_header("Model Comparison", "Compare regression model performance on the held-out test set.")

# ── Load + train ───────────────────────────────────────────────────────────────
@st.cache_resource(show_spinner=False)
def load_all():
    data = {}
    for subject in ["Mathematics", "Portuguese"]:
        df, status = load_uci_dataset(subject)
        if df is not None:
            label = "math" if subject == "Mathematics" else "por"
            res, X_test, y_test = train_all_models(df, label)
            data[subject] = {"results": res, "X_test": X_test, "y_test": y_test, "df": df}
    return data

with st.spinner("Training models…"):
    all_data = load_all()

if not all_data:
    st.error("No datasets available.")
    st.stop()

subj_sel = st.selectbox("Select dataset", list(all_data.keys()), key="mc_subj")
results  = all_data[subj_sel]["results"]
df_ref   = all_data[subj_sel]["df"]
metrics_df = build_metrics_table(results)
best_model = get_best_model(results)

trained_results = {k: v for k, v in results.items() if v["status"] == "trained"}

# ── KPI row ────────────────────────────────────────────────────────────────────
if best_model and trained_results:
    bm  = trained_results[best_model]["test_metrics"]
    lm  = trained_results.get("Linear Regression", {}).get("test_metrics") or bm
    worst_rmse = max(v["test_metrics"]["RMSE"] for v in trained_results.values())

    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.markdown(kpi_card("Best RMSE", str(bm["RMSE"]),
                             f"Best: {best_model}", "trending_down", "icon-green", "kpi-green"),
                    unsafe_allow_html=True)
    with k2:
        st.markdown(kpi_card("Best MAE", str(bm["MAE"]),
                             "Grade points avg error", "straighten", "icon-blue", "kpi-blue"),
                    unsafe_allow_html=True)
    with k3:
        st.markdown(kpi_card("Best R²", str(bm["R2"]),
                             "Variance explained", "trending_up", "icon-teal", "kpi-teal"),
                    unsafe_allow_html=True)
    with k4:
        st.markdown(kpi_card("Models Trained", f"{len(trained_results)} / 4",
                             "All sklearn regressors", "smart_toy", "icon-amber", "kpi-amber"),
                    unsafe_allow_html=True)

    st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)

# ── Metric explanations expander ───────────────────────────────────────────────
with st.expander("What do MAE, RMSE and R² mean?"):
    for key, expl in METRIC_EXPLANATIONS.items():
        st.markdown(f'<div class="insight-box">{expl}</div>', unsafe_allow_html=True)

# ── Results table + bar chart ──────────────────────────────────────────────────
row1_l, row1_r = st.columns([2, 3], gap="medium")

with row1_l:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="chart-title">Test-Set Results</div>'
                '<div class="chart-sub">Best model highlighted</div>', unsafe_allow_html=True)

    def _hl(row):
        return ["background:#EFF6FF;font-weight:700"] * len(row) if row["Model"] == best_model else [""] * len(row)

    show_df = metrics_df.copy()
    show_df.insert(0, "", show_df["Model"].apply(lambda m: "best" if m == best_model else ""))
    st.dataframe(show_df.style.apply(_hl, axis=1),
                 width='stretch', hide_index=True, height=210)
    st.markdown("</div>", unsafe_allow_html=True)

with row1_r:
    st.markdown('<div class="card" style="padding-bottom:10px;">', unsafe_allow_html=True)
    st.markdown('<div class="chart-title">Metric Comparison</div>'
                '<div class="chart-sub">MAE · RMSE · R² across models</div>', unsafe_allow_html=True)

    tr = metrics_df[metrics_df["Status"] == "Trained"].copy()
    if not tr.empty:
        fig_bar = go.Figure()
        for metric, col in [("MAE","#2563EB"), ("RMSE","#D97706"), ("R²","#0D9488")]:
            fig_bar.add_trace(go.Bar(name=metric, x=tr["Model"],
                                     y=tr[metric].astype(float), marker_color=col))
        fig_bar.update_layout(
            barmode="group", height=240, template=CHART_TEMPLATE,
            margin=dict(l=40, r=16, t=8, b=60),
            legend=dict(orientation="h", y=1.10, font=dict(size=11)),
            xaxis=dict(showgrid=False, tickfont=dict(size=10)),
            yaxis=dict(showgrid=True, gridcolor="#F1F5F9"),
            plot_bgcolor="#FFF", paper_bgcolor="#FFF",
        )
        st.plotly_chart(fig_bar, width='stretch', config={"displayModeBar": False})
    st.markdown("</div>", unsafe_allow_html=True)

# ── Detailed analysis ──────────────────────────────────────────────────────────
st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)
st.markdown('<div class="card">', unsafe_allow_html=True)
st.markdown('<div class="chart-title">Detailed Model Analysis</div>', unsafe_allow_html=True)

trained_names = list(trained_results.keys())
detail_model  = st.selectbox("Select model", trained_names,
                             index=trained_names.index(best_model) if best_model in trained_names else 0,
                             key="detail_model")
info = trained_results[detail_model]

d1, d2, d3 = st.columns(3, gap="medium")

with d1:
    st.markdown('<div class="chart-sub">Actual vs Predicted</div>', unsafe_allow_html=True)
    fig_av = actual_vs_predicted(info["y_test"], info["y_pred"], detail_model)
    fig_av.update_layout(height=270, margin=dict(l=48, r=16, t=36, b=48), paper_bgcolor="#FFF")
    st.plotly_chart(fig_av, width='stretch', config={"displayModeBar": False})

with d2:
    st.markdown('<div class="chart-sub">Residual Plot</div>', unsafe_allow_html=True)
    fig_res = residual_plot(info["y_test"], info["y_pred"], detail_model)
    fig_res.update_layout(height=270, margin=dict(l=48, r=16, t=36, b=48), paper_bgcolor="#FFF")
    st.plotly_chart(fig_res, width='stretch', config={"displayModeBar": False})

with d3:
    st.markdown('<div class="chart-sub">Feature Importance</div>', unsafe_allow_html=True)
    feat_names = get_all_feature_columns(df_ref)
    fig_fi = feature_importance(info["pipeline"], feat_names, detail_model, top_n=10)
    fig_fi.update_layout(height=270, margin=dict(l=8, r=56, t=36, b=36), paper_bgcolor="#FFF")
    st.plotly_chart(fig_fi, width='stretch', config={"displayModeBar": False})

st.markdown("</div>", unsafe_allow_html=True)

# ── Train vs Test gap ──────────────────────────────────────────────────────────
st.markdown('<div class="card" style="padding-bottom:6px;">', unsafe_allow_html=True)
st.markdown('<div class="chart-title">Training vs Test RMSE</div>'
            '<div class="chart-sub">Large gap indicates overfitting</div>', unsafe_allow_html=True)

tt_rows = [
    {"Model": k,
     "Train RMSE": v["train_metrics"]["RMSE"],
     "Test RMSE":  v["test_metrics"]["RMSE"]}
    for k, v in trained_results.items()
]
tt_df = pd.DataFrame(tt_rows)
fig_tt = go.Figure([
    go.Bar(name="Train RMSE", x=tt_df["Model"], y=tt_df["Train RMSE"], marker_color="#2563EB"),
    go.Bar(name="Test RMSE",  x=tt_df["Model"], y=tt_df["Test RMSE"],  marker_color="#D97706"),
])
fig_tt.update_layout(
    barmode="group", height=240, template=CHART_TEMPLATE,
    margin=dict(l=40, r=16, t=8, b=60),
    legend=dict(orientation="h", y=1.10, font=dict(size=11)),
    xaxis=dict(showgrid=False, tickfont=dict(size=10)),
    yaxis=dict(title="RMSE", showgrid=True, gridcolor="#F1F5F9"),
    plot_bgcolor="#FFF", paper_bgcolor="#FFF",
)
st.plotly_chart(fig_tt, width='stretch', config={"displayModeBar": False})
st.markdown("</div>", unsafe_allow_html=True)
