"""
2_Dataset_Explorer.py  —  Dataset Explorer
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import streamlit as st
import pandas as pd
import plotly.express as px

from src.data_loader   import load_uci_dataset, UCI_DATASETS
from src.styles        import inject_css, sidebar_nav, page_header, kpi_card
from src.visualizations import (
    grade_distribution, correlation_heatmap,
    categorical_grade_breakdown, CHART_TEMPLATE,
)

st.set_page_config(page_title="Dataset Explorer", page_icon="📊", layout="wide")
inject_css()
sidebar_nav()

page_header("Dataset Explorer", "Examine and understand the student performance data.")

# ── Dataset selector ───────────────────────────────────────────────────────────
c_sel, c_gap = st.columns([2, 4])
with c_sel:
    selected = st.selectbox(
        "Select dataset",
        ["Mathematics", "Portuguese"],
        help="Both come from the same UCI study (Cortez & Silva, 2008).",
    )

df, status = load_uci_dataset(selected)
meta = UCI_DATASETS[selected]

if df is None:
    st.error(status)
    st.stop()

# ── Source attribution card ────────────────────────────────────────────────────
st.markdown(f"""
<div class="card" style="padding:16px 22px;">
    <div style="display:flex; align-items:flex-start; justify-content:space-between; flex-wrap:wrap; gap:10px;">
        <div>
            <div style="font-size:1rem;font-weight:700;color:#0F172A;margin-bottom:6px;
                        display:flex;align-items:center;gap:8px;">
                <span class="material-symbols-rounded"
                      style="font-size:20px;color:#2563EB;
                             font-variation-settings:'FILL' 1,'wght' 400,'GRAD' 0,'opsz' 24;">
                    menu_book
                </span>
                {selected} — {meta['subject']}
            </div>
            <div style="font-size:0.85rem;color:#475569;max-width:680px;">{meta['description']}</div>
        </div>
        <div style="display:flex;flex-wrap:wrap;gap:8px;align-items:center;">
            <span style="background:#DBEAFE;color:#1E40AF;border-radius:20px;padding:4px 12px;font-size:.78rem;font-weight:600;">
                {meta['source']}
            </span>
            <span style="background:#D1FAE5;color:#065F46;border-radius:20px;padding:4px 12px;font-size:.78rem;font-weight:600;">
                {meta['license']}
            </span>
            <span style="background:#FEF3C7;color:#92400E;border-radius:20px;padding:4px 12px;font-size:.78rem;font-weight:600;">
                Target: G3 (0–20)
            </span>
        </div>
    </div>
    <div style="font-size:.78rem;color:#94A3B8;margin-top:8px;display:flex;align-items:center;gap:6px;">
        <span class="material-symbols-rounded" style="font-size:14px;color:#94A3B8;">link</span>
        <a href='{meta['url']}' target='_blank'>{meta['url']}</a>
    </div>
</div>
""", unsafe_allow_html=True)

# ── KPI row ────────────────────────────────────────────────────────────────────
k1, k2, k3, k4 = st.columns(4)
with k1:
    st.markdown(kpi_card("Total Rows", f"{len(df):,}", "student records",
                         "table_rows", "icon-blue", "kpi-blue"), unsafe_allow_html=True)
with k2:
    st.markdown(kpi_card("Columns", str(len(df.columns)), "features + grades",
                         "view_column", "icon-teal", "kpi-teal"), unsafe_allow_html=True)
with k3:
    st.markdown(kpi_card("Missing Values", str(int(df.isnull().sum().sum())),
                         "across all columns",
                         "check_circle", "icon-green", "kpi-green"), unsafe_allow_html=True)
with k4:
    st.markdown(kpi_card("Avg Final Grade", f"{df['G3'].mean():.2f} / 20",
                         f"Min {df['G3'].min()} · Max {df['G3'].max()}",
                         "school", "icon-amber", "kpi-amber"), unsafe_allow_html=True)

st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)

# ── Tabs ───────────────────────────────────────────────────────────────────────
t1, t2, t3, t4, t5 = st.tabs(
    ["Data Preview", "Statistics", "Missing Values", "Grade Charts", "Category Breakdown"]
)

# ── Preview ───────────────────────────────────────────────────────────────────
with t1:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    lc, rc = st.columns([3, 1])
    with lc:
        col_filter = st.multiselect("Columns to display (empty = all)", df.columns.tolist())
    with rc:
        n_rows = st.slider("Rows", 5, min(200, len(df)), 25)

    show_cols = col_filter if col_filter else df.columns.tolist()
    st.dataframe(df[show_cols].head(n_rows), width='stretch')

    st.download_button(
        "Download full dataset as CSV",
        data=df.to_csv(index=False).encode(),
        file_name=f"student_{selected.lower()}.csv",
        mime="text/csv",
    )
    st.markdown("</div>", unsafe_allow_html=True)

# ── Statistics ────────────────────────────────────────────────────────────────
with t2:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="chart-title">Descriptive Statistics (numerical columns)</div>', unsafe_allow_html=True)
    st.dataframe(df.select_dtypes("number").describe().T.round(3), width='stretch')

    st.markdown("<hr class='divider'>", unsafe_allow_html=True)
    st.markdown('<div class="chart-title">Column Information</div>', unsafe_allow_html=True)
    dtype_df = pd.DataFrame({
        "Column":        df.columns,
        "Type":          df.dtypes.astype(str).values,
        "Unique Values": [df[c].nunique() for c in df.columns],
        "Sample":        [", ".join(df[c].astype(str).unique()[:4]) for c in df.columns],
    })
    st.dataframe(dtype_df, width='stretch', hide_index=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ── Missing values ────────────────────────────────────────────────────────────
with t3:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="chart-title">Missing Value Report</div>', unsafe_allow_html=True)
    miss = df.isnull().sum()
    miss_df = pd.DataFrame({
        "Column": miss.index,
        "Missing Count": miss.values,
        "Missing %": (miss / len(df) * 100).round(2).values,
    }).sort_values("Missing Count", ascending=False)

    if miss_df["Missing Count"].sum() == 0:
        st.success("No missing values found in this dataset — ready for modelling.")
    else:
        st.warning(f"Missing values in {(miss_df['Missing Count'] > 0).sum()} column(s).")
        st.dataframe(miss_df[miss_df["Missing Count"] > 0], width='stretch', hide_index=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ── Grade charts ──────────────────────────────────────────────────────────────
with t4:
    gc1, gc2 = st.columns(2)
    with gc1:
        st.markdown('<div class="card" style="padding-bottom:10px;">', unsafe_allow_html=True)
        st.markdown('<div class="chart-title">Grade Distribution</div>'
                    '<div class="chart-sub">G3 final grade (0–20)</div>', unsafe_allow_html=True)
        fig_dist = grade_distribution(df, selected)
        fig_dist.update_layout(
            height=270,
            margin=dict(l=40, r=16, t=8, b=36),
            paper_bgcolor="#FFF", plot_bgcolor="#FFF",
        )
        st.plotly_chart(fig_dist, width='stretch', config={"displayModeBar": False})
        st.markdown("</div>", unsafe_allow_html=True)
    with gc2:
        st.markdown('<div class="card" style="padding-bottom:10px;">', unsafe_allow_html=True)
        st.markdown('<div class="chart-title">Feature Correlation Heatmap</div>'
                    '<div class="chart-sub">G1, G2 excluded</div>', unsafe_allow_html=True)
        fig_corr = correlation_heatmap(df, "")
        fig_corr.update_layout(
            height=270,
            margin=dict(l=8, r=8, t=8, b=8),
            paper_bgcolor="#FFF",
        )
        st.plotly_chart(fig_corr, width='stretch', config={"displayModeBar": False})
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown(
        '<div class="insight-box">Correlation shows linear relationships. '
        "Strong positive correlation with G3 may indicate predictive relevance. "
        "Correlation does not prove causation.</div>",
        unsafe_allow_html=True,
    )

# ── Category breakdown ────────────────────────────────────────────────────────
with t5:
    st.markdown('<div class="card" style="padding-bottom:6px;">', unsafe_allow_html=True)
    cat_cols = df.select_dtypes("object").columns.tolist()
    if cat_cols:
        chosen = st.selectbox("Categorical feature", cat_cols, key="cat_sel")
        fig_cat = categorical_grade_breakdown(df, chosen, selected)
        fig_cat.update_layout(height=280, margin=dict(l=0,r=0,t=40,b=0), paper_bgcolor="#FFF")
        st.plotly_chart(fig_cat, width='stretch', config={"displayModeBar": False})

        vc = df[chosen].value_counts().reset_index()
        vc.columns = [chosen, "Count"]
        st.dataframe(vc, width='stretch', hide_index=True)
    else:
        st.info("No categorical columns found.")
    st.markdown("</div>", unsafe_allow_html=True)
