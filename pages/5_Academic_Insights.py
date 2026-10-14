"""
5_Academic_Insights.py  —  Academic Insights

Empty-card fix: Streamlit auto-closes every st.markdown() HTML fragment, so
<div class="card"> … </div> wrappers that span multiple st.* calls produced
blank boxes. Solution: use st.container() for grouping and render all content
inside it with native widgets; HTML is only used for the card header line.

Chart-title clipping fix: the Plotly figure title was set inside the figure
(title_font_size=16, margin t=8) — not enough room. We now suppress the
Plotly title (title="") and render our own .chart-title header above the
chart. The top margin is set to 4 px, which is correct when there is no
internal title.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from src.data_loader    import load_uci_dataset, get_all_feature_columns
from src.train_models   import train_all_models, get_best_model
from src.styles         import inject_css, sidebar_nav, page_header, mi
from src.visualizations import (
    studytime_vs_grade, absences_vs_grade,
    correlation_heatmap, feature_importance, CHART_TEMPLATE,
)

st.set_page_config(page_title="Academic Insights", page_icon="📊", layout="wide")
inject_css()
sidebar_nav()

# ── Page-specific CSS (scoped, no global side-effects) ─────────────────────────
st.markdown("""
<style>
/* Chart card: white surface, consistent padding, subtle shadow */
.insight-chart-card {
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 12px;
    padding: 16px 18px 8px 18px;
    box-shadow: 0 1px 3px rgba(0,0,0,.05), 0 4px 12px rgba(0,0,0,.04);
    margin-bottom: 16px;
}
/* Compact header row inside each card */
.insight-chart-card .chart-title { margin-bottom: 1px; }
.insight-chart-card .chart-sub   { margin-bottom: 8px; }
</style>
""", unsafe_allow_html=True)

page_header(
    "Academic Insights",
    "Explore relationships between student characteristics and academic performance.",
    icon="insights",
)

# Warning banner
st.markdown(f"""
<div class="warn-box">
    <span class="material-symbols-rounded"
          style="font-size:18px;flex-shrink:0;color:#D97706;
                 font-variation-settings:'FILL' 1,'wght' 400,'GRAD' 0,'opsz' 24;">
        warning
    </span>
    <span><b>Important:</b> These charts show statistical associations, not causal
    relationships. A correlation does not prove that changing one variable will
    change a student's grade.</span>
</div>
""", unsafe_allow_html=True)

# ── Load data ──────────────────────────────────────────────────────────────────
@st.cache_resource(show_spinner=False)
def load_all():
    data = {}
    for subject in ["Mathematics", "Portuguese"]:
        df, status = load_uci_dataset(subject)
        if df is not None:
            label = "math" if subject == "Mathematics" else "por"
            res, _, _ = train_all_models(df, label)
            data[subject] = {"df": df, "results": res}
    return data

with st.spinner("Loading…"):
    all_data = load_all()

if not all_data:
    st.error("No datasets available.")
    st.stop()

subj = st.selectbox("Dataset", list(all_data.keys()), key="ins_subj")
df   = all_data[subj]["df"]
res  = all_data[subj]["results"]

st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)

t1, t2, t3, t4, t5 = st.tabs([
    "Study Time", "Absences", "Subject Grades",
    "Correlations", "Feature Importance",
])

# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — Study Time
# ══════════════════════════════════════════════════════════════════════════════
with t1:
    col_chart, col_stats = st.columns([3, 2], gap="medium")

    # ── Left: chart ───────────────────────────────────────────────────────────
    with col_chart:
        # Card header rendered as a single self-contained HTML block
        st.markdown("""
        <div class="insight-chart-card" style="padding-bottom:4px;">
            <div class="chart-title">Study Time vs Final Grade</div>
            <div class="chart-sub">Weekly study hours grouped by G3 distribution</div>
        </div>
        """, unsafe_allow_html=True)

        # Chart rendered OUTSIDE the card div (it's a native widget).
        # We give it matching visual style via background + margin.
        fig_st = studytime_vs_grade(df, subj)
        fig_st.update_layout(
            title="",          # title shown in our header above — clear Plotly's own
            height=300,
            margin=dict(l=48, r=16, t=4, b=48),
            paper_bgcolor="#FFFFFF",
            plot_bgcolor="#FFFFFF",
        )
        st.plotly_chart(fig_st, width='stretch',
                        config={"displayModeBar": False})

    # ── Right: stats + insight ────────────────────────────────────────────────
    with col_stats:
        st.markdown("""
        <div class="insight-chart-card" style="padding-bottom:4px;">
            <div class="chart-title">Aggregate Statistics</div>
            <div class="chart-sub">Mean · Median · Count by study-time band</div>
        </div>
        """, unsafe_allow_html=True)

        labels = {1: "< 2 hrs", 2: "2–5 hrs", 3: "5–10 hrs", 4: "> 10 hrs"}
        agg = (
            df.groupby("studytime")["G3"]
            .agg(["mean", "median", "count"])
            .round(2)
            .reset_index()
        )
        agg["studytime"] = agg["studytime"].map(labels)
        agg.columns = ["Study Time", "Mean G3", "Median G3", "Count"]
        st.dataframe(agg, width='stretch', hide_index=True)

        st.markdown(f"""
        <div class="insight-box" style="margin-top:10px;">
            <span class="material-symbols-rounded"
                  style="font-size:16px;flex-shrink:0;color:#2563EB;
                         font-variation-settings:'FILL' 1,'wght' 400,'GRAD' 0,'opsz' 24;">
                info
            </span>
            <span>Students who study more hours per week generally score higher
            on average. However, many other factors also contribute to academic
            outcomes.</span>
        </div>
        """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — Absences
# ══════════════════════════════════════════════════════════════════════════════
with t2:
    col_chart2, col_stats2 = st.columns([3, 2], gap="medium")

    with col_chart2:
        st.markdown("""
        <div class="insight-chart-card" style="padding-bottom:4px;">
            <div class="chart-title">Absences vs Final Grade</div>
            <div class="chart-sub">Each dot is one student · OLS trend line</div>
        </div>
        """, unsafe_allow_html=True)

        fig_ab = absences_vs_grade(df, subj)
        fig_ab.update_layout(
            title="",
            height=300,
            margin=dict(l=48, r=16, t=4, b=48),
            paper_bgcolor="#FFFFFF",
            plot_bgcolor="#FFFFFF",
        )
        st.plotly_chart(fig_ab, width='stretch',
                        config={"displayModeBar": False})

    with col_stats2:
        corr_val = df["absences"].corr(df["G3"])

        st.markdown("""
        <div class="insight-chart-card" style="padding-bottom:4px;">
            <div class="chart-title">Absence Bands</div>
            <div class="chart-sub">Mean grade and count per absence range</div>
        </div>
        """, unsafe_allow_html=True)

        bins   = [0, 5, 10, 20, 93]
        blabel = ["0–4", "5–9", "10–19", "20+"]
        df2    = df.copy()
        df2["Band"] = pd.cut(df2["absences"], bins=bins, labels=blabel, right=False)
        ab_agg = (
            df2.groupby("Band", observed=True)["G3"]
            .agg(["mean", "count"])
            .round(2)
            .reset_index()
        )
        ab_agg.columns = ["Absences", "Mean G3", "Count"]
        st.dataframe(ab_agg, width='stretch', hide_index=True)

        st.markdown(f"""
        <div class="insight-box" style="margin-top:10px;">
            <span class="material-symbols-rounded"
                  style="font-size:16px;flex-shrink:0;color:#2563EB;
                         font-variation-settings:'FILL' 1,'wght' 400,'GRAD' 0,'opsz' 24;">
                info
            </span>
            <span>Pearson r = <b>{corr_val:.3f}</b>. Higher absences are
            associated with lower grades in this dataset. Individual
            variation is large.</span>
        </div>
        """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — Subject Grades
# ══════════════════════════════════════════════════════════════════════════════
with t3:
    st.markdown("""
    <div class="insight-chart-card" style="padding-bottom:4px;">
        <div class="chart-title">Grade Distribution by Subject</div>
        <div class="chart-sub">Violin + box plot &nbsp;·&nbsp; G3 final grade (0–20)</div>
    </div>
    """, unsafe_allow_html=True)

    frames = [d["df"][["G3"]].assign(Subject=s) for s, d in all_data.items()]
    if len(frames) > 1:
        cdf    = pd.concat(frames, ignore_index=True)
        fig_vl = px.violin(
            cdf, x="Subject", y="G3", color="Subject",
            box=True, points="outliers",
            color_discrete_map={"Mathematics": "#2563EB", "Portuguese": "#0D9488"},
            template=CHART_TEMPLATE,
        )
        fig_vl.update_layout(
            title="",
            height=320, showlegend=False,
            margin=dict(l=48, r=16, t=4, b=48),
            xaxis=dict(title=""),
            yaxis=dict(title="Final Grade (G3)", showgrid=True,
                       gridcolor="#F1F5F9"),
            paper_bgcolor="#FFFFFF", plot_bgcolor="#FFFFFF",
        )
        st.plotly_chart(fig_vl, width='stretch',
                        config={"displayModeBar": False})
    else:
        fig_v1 = px.violin(
            df, y="G3", box=True, template=CHART_TEMPLATE,
            color_discrete_sequence=["#2563EB"],
        )
        fig_v1.update_layout(
            title="",
            height=320, margin=dict(l=48, r=16, t=4, b=48),
            paper_bgcolor="#FFFFFF", plot_bgcolor="#FFFFFF",
        )
        st.plotly_chart(fig_v1, width='stretch',
                        config={"displayModeBar": False})

    st.markdown("""
    <div class="insight-box">
        <span class="material-symbols-rounded"
              style="font-size:16px;flex-shrink:0;color:#2563EB;
                     font-variation-settings:'FILL' 1,'wght' 400,'GRAD' 0,'opsz' 24;">
            info
        </span>
        <span>Portuguese students score slightly higher on average. Both datasets
        are from the same two schools (Cortez &amp; Silva, 2008).</span>
    </div>
    """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 4 — Correlations
# ══════════════════════════════════════════════════════════════════════════════
with t4:
    c4l, c4r = st.columns([2, 1], gap="medium")

    with c4l:
        st.markdown(f"""
        <div class="insight-chart-card" style="padding-bottom:4px;">
            <div class="chart-title">Correlation Matrix — {subj}</div>
            <div class="chart-sub">G1, G2 excluded &nbsp;·&nbsp; Pearson r</div>
        </div>
        """, unsafe_allow_html=True)

        fig_ch = correlation_heatmap(df, "")
        fig_ch.update_layout(
            title="",
            height=400,
            margin=dict(l=8, r=8, t=4, b=8),
            paper_bgcolor="#FFFFFF",
        )
        st.plotly_chart(fig_ch, width='stretch',
                        config={"displayModeBar": False})

    with c4r:
        st.markdown("""
        <div class="insight-chart-card" style="padding-bottom:4px;">
            <div class="chart-title">Top Correlators with G3</div>
            <div class="chart-sub">Sorted by absolute Pearson r</div>
        </div>
        """, unsafe_allow_html=True)

        num_df = df.select_dtypes("number").drop(columns=["G1", "G2"],
                                                  errors="ignore")
        top_c = (
            num_df.corr()["G3"]
            .drop("G3")
            .sort_values(key=abs, ascending=False)
            .head(8)
            .reset_index()
        )
        top_c.columns = ["Feature", "r"]
        top_c["r"]    = top_c["r"].round(3)
        top_c["Direction"] = top_c["r"].apply(
            lambda x: "Positive" if x > 0 else "Negative"
        )
        st.dataframe(top_c, width='stretch', hide_index=True)

        st.markdown("""
        <div class="insight-box" style="margin-top:10px;">
            <span class="material-symbols-rounded"
                  style="font-size:16px;flex-shrink:0;color:#2563EB;
                         font-variation-settings:'FILL' 1,'wght' 400,'GRAD' 0,'opsz' 24;">
                info
            </span>
            <span>Correlation shows linear association only. Non-linear
            relationships may not appear here.</span>
        </div>
        """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 5 — Feature Importance
# ══════════════════════════════════════════════════════════════════════════════
with t5:
    tree_models = {
        k: v for k, v in res.items()
        if v["status"] == "trained"
        and k in ["Random Forest", "Gradient Boosting", "Decision Tree"]
    }

    if not tree_models:
        st.info("No tree-based models available.")
    else:
        fi_sel_col, _ = st.columns([2, 3])
        with fi_sel_col:
            model_choice = st.selectbox(
                "Model", list(tree_models.keys()), key="fi_model"
            )

        st.markdown(f"""
        <div class="insight-chart-card" style="padding-bottom:4px;">
            <div class="chart-title">Feature Importance — {model_choice}</div>
            <div class="chart-sub">Top 15 features by split gain · {subj}</div>
        </div>
        """, unsafe_allow_html=True)

        feat_names = get_all_feature_columns(df)
        fig_fi = feature_importance(
            tree_models[model_choice]["pipeline"],
            feat_names, model_choice, top_n=15,
        )
        fig_fi.update_layout(
            title="",
            height=380,
            margin=dict(l=8, r=64, t=4, b=36),
            paper_bgcolor="#FFFFFF",
        )
        st.plotly_chart(fig_fi, width='stretch',
                        config={"displayModeBar": False})

        st.markdown("""
        <div class="insight-box">
            <span class="material-symbols-rounded"
                  style="font-size:16px;flex-shrink:0;color:#2563EB;
                         font-variation-settings:'FILL' 1,'wght' 400,'GRAD' 0,'opsz' 24;">
                info
            </span>
            <span>Feature importance shows which variables reduced prediction
            error most. Higher importance does not imply a causal effect — many
            important features are not directly actionable.</span>
        </div>
        """, unsafe_allow_html=True)

    # ── Past failures bonus chart ──────────────────────────────────────────
    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    st.markdown("""
    <div class="insight-chart-card" style="padding-bottom:4px;">
        <div class="chart-title">Past Failures vs Final Grade</div>
        <div class="chart-sub">Box plot &nbsp;·&nbsp; 0 = never failed a class</div>
    </div>
    """, unsafe_allow_html=True)

    fig_pf = px.box(
        df, x="failures", y="G3",
        color="failures",
        color_discrete_sequence=px.colors.sequential.Blues_r,
        labels={"failures": "Past Class Failures", "G3": "Final Grade (G3)"},
        template=CHART_TEMPLATE,
    )
    fig_pf.update_layout(
        title="",
        height=280, showlegend=False,
        margin=dict(l=48, r=16, t=4, b=48),
        xaxis=dict(title="Past Class Failures"),
        yaxis=dict(title="Final Grade (G3)", showgrid=True,
                   gridcolor="#F1F5F9"),
        paper_bgcolor="#FFFFFF", plot_bgcolor="#FFFFFF",
    )
    st.plotly_chart(fig_pf, width='stretch',
                        config={"displayModeBar": False})

