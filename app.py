"""
app.py  —  Overview Dashboard
Student Performance Analytics & Prediction System

Empty-card fix: st.markdown('<div class="card">') auto-closes immediately
in Streamlit, so any subsequent st.* widgets render outside it and a blank
box appears above them. Every card header is now a single self-contained
HTML block; native widgets follow directly without being "inside" the HTML.
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

from src.data_loader   import load_uci_dataset, get_all_feature_columns
from src.train_models  import train_all_models, get_best_model, build_metrics_table
from src.styles        import inject_css, sidebar_nav, kpi_card, mi
from src.visualizations import CHART_TEMPLATE

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Student Performance Analytics",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)
inject_css()
sidebar_nav()

# ── Shared card-header CSS (scoped, no side-effects on other pages) ────────────
st.markdown("""
<style>
/* Self-contained card header block — used above every native widget group */
.ov-card-hdr {
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 12px 12px 0 0;
    padding: 14px 18px 10px 18px;
    box-shadow: 0 1px 3px rgba(0,0,0,.04);
    margin-bottom: 0;
}
/* Card body — sits flush below its header */
.ov-card-body {
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-top: none;
    border-radius: 0 0 12px 12px;
    padding: 8px 14px 14px 14px;
    box-shadow: 0 1px 3px rgba(0,0,0,.04);
    margin-bottom: 16px;
}
/* Single-piece card (header + body merged, no native widgets inside) */
.ov-card {
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 12px;
    padding: 16px 18px 12px 18px;
    box-shadow: 0 1px 3px rgba(0,0,0,.04);
    margin-bottom: 16px;
}
</style>
""", unsafe_allow_html=True)

# ── Load + train ───────────────────────────────────────────────────────────────
@st.cache_resource(show_spinner=False)
def load_and_train():
    datasets, model_results = {}, {}
    for subject in ["Mathematics", "Portuguese"]:
        df, status = load_uci_dataset(subject)
        if df is not None:
            datasets[subject] = df
            label = "math" if subject == "Mathematics" else "por"
            res, _, _ = train_all_models(df, label)
            model_results[subject] = res
    return datasets, model_results

with st.spinner("Loading data and training models — please wait…"):
    datasets, model_results = load_and_train()

if not datasets:
    st.error(
        "No datasets loaded. Place `student-mat.csv` and `student-por.csv` "
        "in the `data/` folder then restart. See `data/README.md` for instructions."
    )
    st.stop()

# ── Derived KPI values ─────────────────────────────────────────────────────────
total_records   = sum(len(d) for d in datasets.values())
n_datasets      = len(datasets)
first_df        = next(iter(datasets.values()))
n_features      = len(get_all_feature_columns(first_df))
all_g3          = pd.concat([d["G3"] for d in datasets.values()])
avg_grade       = round(all_g3.mean(), 1)
pass_rate       = round((all_g3 >= 10).mean() * 100, 1)
at_risk         = int((all_g3 < 10).sum())
best_model_name = "—"
best_rmse_val   = None

for subject, results in model_results.items():
    best = get_best_model(results)
    if best and results[best]["test_metrics"]:
        r = results[best]["test_metrics"]["RMSE"]
        if best_rmse_val is None or r < best_rmse_val:
            best_rmse_val   = r
            best_model_name = best

# ══════════════════════════════════════════════════════════════════
# ROW 1 — Page header
# ══════════════════════════════════════════════════════════════════
hdr_l, hdr_r = st.columns([3, 1])
with hdr_l:
    st.markdown("""
    <h1 style="font-size:1.8rem;font-weight:800;color:#172033;
               letter-spacing:-.3px;margin:0 0 2px 0;">
        Education Analytics Dashboard
    </h1>
    <p style="color:#64748B;font-size:0.88rem;margin:0 0 18px 0;">
        Data-driven insights into student achievement
        &nbsp;·&nbsp; UCI Student Performance Dataset
    </p>
    """, unsafe_allow_html=True)
with hdr_r:
    st.markdown(f"""
    <div style="display:flex;justify-content:flex-end;align-items:center;
                gap:8px;padding-top:6px;">
        <div style="background:#FFF;border:1px solid #E2E8F0;border-radius:8px;
                    padding:6px 14px;font-size:0.82rem;color:#475569;font-weight:500;
                    display:flex;align-items:center;gap:6px;">
            {mi("tune","16px","#475569")} Filters
        </div>
        <div style="background:#FFF;border:1px solid #E2E8F0;border-radius:8px;
                    padding:6px 14px;font-size:0.82rem;color:#475569;font-weight:500;
                    display:flex;align-items:center;gap:6px;">
            {mi("calendar_month","16px","#475569")} UCI · 2005–06
        </div>
    </div>
    """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════
# ROW 2 — KPI cards
# ══════════════════════════════════════════════════════════════════
k1, k2, k3, k4 = st.columns(4, gap="small")
with k1:
    st.markdown(kpi_card(
        "Pass Rate", f"{pass_rate}%",
        "Grade >= 10 / 20  ·  Target Met",
        "check_circle", "icon-green", "kpi-green",
    ), unsafe_allow_html=True)
with k2:
    st.markdown(kpi_card(
        "Average Grade", str(avg_grade),
        "G3 out of 20 — both subjects",
        "school", "icon-blue", "kpi-blue",
    ), unsafe_allow_html=True)
with k3:
    st.markdown(kpi_card(
        "Total Students", f"{total_records:,}",
        f"{n_datasets} datasets · {n_features} features",
        "groups", "icon-teal", "kpi-teal",
    ), unsafe_allow_html=True)
with k4:
    st.markdown(kpi_card(
        "At-Risk Students", str(at_risk),
        "Grade below 10 / 20",
        "flag", "icon-red", "kpi-red",
    ), unsafe_allow_html=True)

st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════
# ROW 3 — Three chart cards
# Each card: self-contained HTML header → native plotly_chart below
# ══════════════════════════════════════════════════════════════════
c1, c2, c3 = st.columns([2.1, 2.1, 1.8], gap="medium")

# ── Chart 1: Grade Distribution ───────────────────────────────────
with c1:
    st.markdown("""
    <div class="ov-card-hdr">
        <div class="chart-title">Student Grade Distribution</div>
        <div class="chart-sub">G3 final grade (0–20) · both subjects</div>
    </div>
    """, unsafe_allow_html=True)

    colors = {"Mathematics": "#2563EB", "Portuguese": "#0D9488"}
    fills  = {"Mathematics": "rgba(37,99,235,0.10)",
              "Portuguese":  "rgba(13,148,136,0.10)"}
    fig1 = go.Figure()
    for subj, df in datasets.items():
        counts = df["G3"].value_counts().sort_index()
        grades = list(range(0, 21))
        freq   = [counts.get(g, 0) for g in grades]
        fig1.add_trace(go.Scatter(
            x=grades, y=freq, mode="lines+markers", name=subj,
            line=dict(color=colors[subj], width=2.5),
            marker=dict(size=5, color=colors[subj]),
            fill="tozeroy", fillcolor=fills[subj],
        ))
    fig1.update_layout(
        template=CHART_TEMPLATE, height=230,
        margin=dict(l=40, r=16, t=6, b=48),
        legend=dict(orientation="h", y=-0.28, x=0, font=dict(size=11)),
        xaxis=dict(title="Grade (G3)", tickmode="array",
                   tickvals=list(range(0, 21, 2)),
                   showgrid=True, gridcolor="#F1F5F9"),
        yaxis=dict(title="Students", showgrid=True, gridcolor="#F1F5F9"),
        plot_bgcolor="#FFFFFF", paper_bgcolor="#FFFFFF",
    )
    st.plotly_chart(fig1, width='stretch',
                    config={"displayModeBar": False})

# ── Chart 2: Avg Grade by Study Time ──────────────────────────────
with c2:
    st.markdown("""
    <div class="ov-card-hdr">
        <div class="chart-title">Average Grade by Study Time</div>
        <div class="chart-sub">Weekly study hours vs mean final grade (G3)</div>
    </div>
    """, unsafe_allow_html=True)

    study_labels = {1: "< 2 hrs", 2: "2–5 hrs", 3: "5–10 hrs", 4: "> 10 hrs"}
    combined_df  = pd.concat(datasets.values(), ignore_index=True)
    agg = combined_df.groupby("studytime")["G3"].mean().reset_index()
    agg["label"] = agg["studytime"].map(study_labels)
    bar_colors   = ["#2563EB", "#38BDF8", "#0D9488", "#059669"]

    fig2 = go.Figure(go.Bar(
        x=agg["label"], y=agg["G3"].round(1),
        marker_color=bar_colors[:len(agg)],
        text=agg["G3"].round(1),
        textposition="outside",
        textfont=dict(size=11, color="#172033"),
        width=0.55,
    ))
    fig2.update_layout(
        template=CHART_TEMPLATE, height=230,
        margin=dict(l=40, r=16, t=6, b=36),
        xaxis=dict(title="Study Time per Week", showgrid=False),
        yaxis=dict(title="Mean G3", range=[0, 22],
                   showgrid=True, gridcolor="#F1F5F9"),
        plot_bgcolor="#FFFFFF", paper_bgcolor="#FFFFFF",
    )
    st.plotly_chart(fig2, width='stretch',
                    config={"displayModeBar": False})

# ── Chart 3: Model RMSE ────────────────────────────────────────────
with c3:
    st.markdown("""
    <div class="ov-card-hdr">
        <div class="chart-title">Model RMSE</div>
        <div class="chart-sub">Test-set · lower is better</div>
    </div>
    """, unsafe_allow_html=True)

    color_map = {
        "Linear Regression": "#F59E0B",
        "Decision Tree":     "#EF4444",
        "Random Forest":     "#0D9488",
        "Gradient Boosting": "#2563EB",
    }
    model_names, rmse_vals, bar_cols = [], [], []
    if model_results:
        first_res = next(iter(model_results.values()))
        for mn, info in first_res.items():
            if info["status"] == "trained":
                model_names.append(mn)
                rmse_vals.append(info["test_metrics"]["RMSE"])
                bar_cols.append(color_map.get(mn, "#94A3B8"))

    if model_names:
        fig3 = go.Figure(go.Bar(
            x=rmse_vals, y=model_names,
            orientation="h",
            marker_color=bar_cols,
            text=[f"{v:.2f}" for v in rmse_vals],
            textposition="outside",
            textfont=dict(size=11, color="#172033"),
        ))
        fig3.update_layout(
            template=CHART_TEMPLATE, height=230,
            margin=dict(l=8, r=52, t=6, b=36),
            xaxis=dict(title="RMSE (grade points)", showgrid=True,
                       gridcolor="#F1F5F9",
                       range=[0, max(rmse_vals) * 1.30]),
            yaxis=dict(title="", autorange="reversed", showgrid=False,
                       tickfont=dict(size=11)),
            plot_bgcolor="#FFFFFF", paper_bgcolor="#FFFFFF",
        )
        st.plotly_chart(fig3, width='stretch',
                        config={"displayModeBar": False})

st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════
# ROW 4 — Model Evaluation Summary + Grade by Subject
# Each section: self-contained HTML header → native widget below
# ══════════════════════════════════════════════════════════════════
row4_l, row4_r = st.columns([3, 2], gap="medium")

# ── Left: Model Evaluation Summary ────────────────────────────────
with row4_l:
    st.markdown("""
    <div class="ov-card-hdr">
        <div class="chart-title">Model Evaluation Summary</div>
        <div class="chart-sub">
            Test-set MAE · RMSE · R² · Best model highlighted
            &nbsp;·&nbsp; Lower RMSE / MAE = better · Higher R² = better
        </div>
    </div>
    """, unsafe_allow_html=True)

    subj_sel = st.selectbox(
        "Subject", list(model_results.keys()),
        key="ov_subj", label_visibility="collapsed",
    )

    if subj_sel in model_results:
        mt   = build_metrics_table(model_results[subj_sel])
        best = get_best_model(model_results[subj_sel])

        def _style_row(row):
            if row["Model"] == best:
                return ["background-color:#EFF6FF;font-weight:700"] * len(row)
            return [""] * len(row)

        st.dataframe(
            mt.style.apply(_style_row, axis=1),
            width='stretch', hide_index=True, height=190,
        )
        if best:
            m = model_results[subj_sel][best]["test_metrics"]
            st.markdown(
                f'<div class="insight-box">'
                f'<span class="material-symbols-rounded" '
                f'style="font-size:16px;flex-shrink:0;'
                f'font-variation-settings:\'FILL\' 1,\'wght\' 400,\'GRAD\' 0,\'opsz\' 24;">'
                f'star</span>'
                f' Best: <b>{best}</b> — '
                f'RMSE {m["RMSE"]}, MAE {m["MAE"]}, R² {m["R2"]}'
                " · Selected by lowest test-set RMSE.</div>",
                unsafe_allow_html=True,
            )

# ── Right: Grade by Subject ────────────────────────────────────────
with row4_r:
    st.markdown("""
    <div class="ov-card-hdr">
        <div class="chart-title">Grade by Subject</div>
        <div class="chart-sub">Median and spread · G3 (0–20)</div>
    </div>
    """, unsafe_allow_html=True)

    frames = [d[["G3"]].assign(Subject=s) for s, d in datasets.items()]
    if frames:
        cdf  = pd.concat(frames, ignore_index=True)
        fig4 = px.box(
            cdf, x="Subject", y="G3", color="Subject",
            color_discrete_map={"Mathematics": "#2563EB", "Portuguese": "#0D9488"},
            template=CHART_TEMPLATE,
        )
        fig4.update_layout(
            height=260,
            margin=dict(l=40, r=16, t=6, b=36),
            showlegend=False,
            xaxis=dict(title="", showgrid=False),
            yaxis=dict(title="Final Grade (G3)",
                       showgrid=True, gridcolor="#F1F5F9"),
            plot_bgcolor="#FFFFFF", paper_bgcolor="#FFFFFF",
        )
        st.plotly_chart(fig4, width='stretch',
                        config={"displayModeBar": False})

# ── Disclaimer ─────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="warn-box">
    <span class="material-symbols-rounded"
          style="font-size:18px;flex-shrink:0;color:#D97706;
                 font-variation-settings:'FILL' 1,'wght' 400,'GRAD' 0,'opsz' 24;">
        warning
    </span>
    <span>This system is an <b>educational demonstration tool</b>.
    Predictions are statistical estimates and must not be used to make
    high-stakes decisions about individual students.</span>
</div>
""", unsafe_allow_html=True)
