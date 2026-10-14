"""
6_About.py  —  About the Project
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import streamlit as st
from src.styles import inject_css, sidebar_nav, page_header

st.set_page_config(page_title="About", page_icon="ℹ️", layout="wide")
inject_css()
sidebar_nav()

page_header("About the Project",
            "Dataset sources, methodology, technology stack, and responsible use statement.")

t1, t2, t3, t4, t5 = st.tabs(
    ["Overview", "Datasets", "Methodology", "Technology", "Responsible Use"]
)

# ─── Overview ─────────────────────────────────────────────────────────────────
with t1:
    st.markdown("""
    <div class="card">
        <div class="chart-title">Project Abstract</div>
        <p style="font-size:.9rem;color:#374151;line-height:1.7;margin-top:10px;">
        The <b>Student Performance Analytics &amp; Prediction System</b> is an interactive educational
        analytics application developed as an academic internship project. It analyses historical
        student data from Portuguese secondary schools, identifies patterns associated with academic
        performance, compares machine learning regression models, and estimates student final grades
        through a professional Streamlit dashboard.
        </p>
    </div>

    <div class="card">
        <div class="chart-title">Objectives</div>
        <ul style="font-size:.9rem;color:#374151;line-height:2;margin-top:10px;">
            <li>Acquire and validate real, publicly available student performance data</li>
            <li>Perform exploratory data analysis and visualise key patterns</li>
            <li>Build a scikit-learn preprocessing pipeline</li>
            <li>Train and compare four regression models (Linear Regression, Decision Tree,
                Random Forest, Gradient Boosting)</li>
            <li>Evaluate models fairly on a held-out test set using MAE, RMSE, R²</li>
            <li>Provide an interactive grade estimation form</li>
            <li>Demonstrate responsible interpretation of machine learning predictions</li>
        </ul>
    </div>

    <div class="card">
        <div class="chart-title">Known Limitations</div>
        <ul style="font-size:.9rem;color:#374151;line-height:2;margin-top:10px;">
            <li>Dataset covers only two Portuguese schools, 2005–2006 — may not generalise</li>
            <li>G1 and G2 excluded by design; including them would substantially raise R²</li>
            <li>No hyperparameter tuning applied</li>
            <li>OULAD is a documented future extension, not in this version</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

# ─── Datasets ─────────────────────────────────────────────────────────────────
with t2:
    st.markdown("""
    <div class="card">
        <div class="chart-title">UCI Student Performance Dataset</div>
        <table style="width:100%;border-collapse:collapse;font-size:.88rem;margin-top:12px;">
        <tr style="background:#F8FAFC;">
            <th style="padding:9px 12px;text-align:left;color:#64748B;font-weight:600;border-bottom:1px solid #E2E8F0;">Property</th>
            <th style="padding:9px 12px;text-align:left;color:#64748B;font-weight:600;border-bottom:1px solid #E2E8F0;">Details</th>
        </tr>
        <tr><td style="padding:9px 12px;border-bottom:1px solid #F1F5F9;font-weight:600;">Source</td><td style="padding:9px 12px;border-bottom:1px solid #F1F5F9;">UCI Machine Learning Repository</td></tr>
        <tr><td style="padding:9px 12px;border-bottom:1px solid #F1F5F9;font-weight:600;">URL</td><td style="padding:9px 12px;border-bottom:1px solid #F1F5F9;"><a href="https://archive.ics.uci.edu/dataset/320/student+performance">archive.ics.uci.edu/dataset/320/student+performance</a></td></tr>
        <tr><td style="padding:9px 12px;border-bottom:1px solid #F1F5F9;font-weight:600;">Citation</td><td style="padding:9px 12px;border-bottom:1px solid #F1F5F9;">Cortez &amp; Silva, FUBUTEC 2008</td></tr>
        <tr><td style="padding:9px 12px;border-bottom:1px solid #F1F5F9;font-weight:600;">License</td><td style="padding:9px 12px;border-bottom:1px solid #F1F5F9;">CC BY 4.0</td></tr>
        <tr><td style="padding:9px 12px;border-bottom:1px solid #F1F5F9;font-weight:600;">Mathematics</td><td style="padding:9px 12px;border-bottom:1px solid #F1F5F9;">395 student records · student-mat.csv</td></tr>
        <tr><td style="padding:9px 12px;border-bottom:1px solid #F1F5F9;font-weight:600;">Portuguese</td><td style="padding:9px 12px;border-bottom:1px solid #F1F5F9;">649 student records · student-por.csv</td></tr>
        <tr><td style="padding:9px 12px;border-bottom:1px solid #F1F5F9;font-weight:600;">Features</td><td style="padding:9px 12px;border-bottom:1px solid #F1F5F9;">30 input features (demographic, social, academic) + G1, G2, G3</td></tr>
        <tr><td style="padding:9px 12px;border-bottom:1px solid #F1F5F9;font-weight:600;">Target</td><td style="padding:9px 12px;border-bottom:1px solid #F1F5F9;">G3 — Final period grade (0–20 scale)</td></tr>
        <tr><td style="padding:9px 12px;font-weight:600;">Delimiter</td><td style="padding:9px 12px;">Semicolon ( ; )</td></tr>
        </table>
    </div>

    <div class="card">
        <div class="chart-title">Manual Download Instructions</div>
        <ol style="font-size:.9rem;color:#374151;line-height:2;margin-top:10px;">
            <li>Visit <a href="https://archive.ics.uci.edu/dataset/320/student+performance">https://archive.ics.uci.edu/dataset/320/student+performance</a></li>
            <li>Click <b>Download</b> to get the ZIP file</li>
            <li>Extract the outer ZIP → find inner <code>student.zip</code></li>
            <li>Extract <code>student.zip</code> → find <code>student-mat.csv</code> and <code>student-por.csv</code></li>
            <li>Place both files in the <code>data/</code> folder and restart the app</li>
        </ol>
    </div>
    """, unsafe_allow_html=True)

# ─── Methodology ──────────────────────────────────────────────────────────────
with t3:
    st.markdown("""
    <div class="card">
        <div class="chart-title">Complete Pipeline</div>
        <div style="font-size:.88rem;color:#374151;line-height:1.8;margin-top:10px;">
            <b>1. Data Acquisition</b> — Automatic download from UCI, or manual file placement<br>
            <b>2. Validation</b> — Confirm semicolon delimiter, G3 column, row count<br>
            <b>3. EDA</b> — Distributions, correlations, missing values, categorical breakdowns<br>
            <b>4. Feature Selection</b> — 13 numerical + 17 categorical; G1, G2, G3 excluded from inputs<br>
            <b>5. Preprocessing</b><br>
            &nbsp;&nbsp;&nbsp;• Numeric: median imputation → StandardScaler<br>
            &nbsp;&nbsp;&nbsp;• Categorical: constant imputation ("missing") → OneHotEncoder(handle_unknown="ignore")<br>
            &nbsp;&nbsp;&nbsp;• Combined via ColumnTransformer — fit only on training set<br>
            <b>6. Train/Test Split</b> — 80/20, random_state=42<br>
            <b>7. Model Training</b> — Linear Regression, Decision Tree, Random Forest, Gradient Boosting<br>
            <b>8. Evaluation</b> — MAE, RMSE, R² on held-out test set only<br>
            <b>9. Best Model Selection</b> — Lowest test-set RMSE<br>
            <b>10. Prediction</b> — User input → same pipeline → predicted G3, clipped [0, 20]
        </div>
    </div>

    <div class="card">
        <div class="chart-title">Why exclude G1 and G2?</div>
        <p style="font-size:.9rem;color:#374151;line-height:1.7;margin-top:10px;">
        Including first and second period grades (G1, G2) as input features would produce
        a much higher R² because intermediate grades are strongly correlated with the final
        grade. We exclude them to model the more realistic and useful scenario: estimating
        a student's likely final grade using only characteristics known at the start of the year.
        </p>
    </div>
    """, unsafe_allow_html=True)

# ─── Technology ───────────────────────────────────────────────────────────────
with t4:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="chart-title">Technology Stack</div>', unsafe_allow_html=True)
    tech = [
        ("Python 3.11+",      "#DBEAFE","#1E40AF",  "Core language"),
        ("Streamlit 1.35+",   "#D1FAE5","#065F46",  "Dashboard framework"),
        ("pandas 2.0+",       "#FEF3C7","#92400E",  "Data manipulation"),
        ("NumPy 1.24+",       "#E0E7FF","#3730A3",  "Numerical computing"),
        ("scikit-learn 1.3+", "#FCE7F3","#9D174D",  "ML pipeline + models"),
        ("Plotly 5.0+",       "#CCFBF1","#0F766E",  "Interactive charts"),
        ("joblib 1.3+",       "#FEE2E2","#991B1B",  "Model persistence"),
        ("requests 2.28+",    "#F3F4F6","#374151",  "Auto dataset download"),
    ]
    cols = st.columns(4)
    for i, (name, bg, color, desc) in enumerate(tech):
        with cols[i % 4]:
            st.markdown(f"""
            <div style="background:{bg};border-radius:10px;padding:14px 16px;margin-bottom:12px;">
                <div style="font-size:.85rem;font-weight:700;color:{color};">{name}</div>
                <div style="font-size:.78rem;color:#374151;margin-top:4px;">{desc}</div>
            </div>
            """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("""
    <div class="card">
        <div class="chart-title">Project Structure</div>
        <pre style="background:#F8FAFC;padding:16px;border-radius:10px;
                    font-size:.82rem;color:#334155;line-height:1.7;overflow-x:auto;">
student_performance_analytics/
├── app.py                        ← Entry point / Overview Dashboard
├── requirements.txt
├── data/
│   ├── student-mat.csv           ← UCI Mathematics (395 records)
│   └── student-por.csv           ← UCI Portuguese (649 records)
├── models/
│   └── *.pkl                     ← Saved pipelines
├── src/
│   ├── data_loader.py            ← Dataset loading &amp; metadata
│   ├── preprocessing.py          ← ColumnTransformer pipeline
│   ├── train_models.py           ← Training &amp; evaluation
│   ├── evaluation.py             ← Metrics &amp; grade bands
│   ├── predictions.py            ← Single-student inference
│   ├── visualizations.py         ← Plotly chart builders
│   └── styles.py                 ← Shared CSS &amp; HTML helpers
└── pages/
    ├── 2_Dataset_Explorer.py
    ├── 3_Performance_Prediction.py
    ├── 4_Model_Comparison.py
    ├── 5_Academic_Insights.py
    └── 6_About.py
        </pre>
    </div>
    """, unsafe_allow_html=True)

# ─── Responsible Use ──────────────────────────────────────────────────────────
with t5:
    st.markdown("""
    <div class="warn-box" style="font-size:.95rem;">
        <b>This system is an educational demonstration tool, not a validated decision-support system.</b>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="card" style="margin-top:12px;">
        <div class="chart-title">Responsible Use Statement</div>
        <p style="font-size:.9rem;color:#374151;line-height:1.8;margin-top:10px;">
        Predictions produced by this system are statistical estimates derived from a limited
        dataset of students from two Portuguese schools in 2005–2006. They must not be used to:
        </p>
        <ul style="font-size:.9rem;color:#374151;line-height:2;">
            <li>Make admissions, placement, or retention decisions about individual students</li>
            <li>Label students as likely to fail or succeed</li>
            <li>Replace professional educational assessment or counselling</li>
            <li>Inform policy without thorough independent validation</li>
        </ul>
        <p style="font-size:.9rem;color:#374151;line-height:1.8;margin-top:8px;">
        Many factors that influence student outcomes — including teaching quality, mental health,
        learning disabilities, and socioeconomic circumstances — are absent from this dataset.
        </p>
    </div>

    <div class="card">
        <div class="chart-title">Dataset Attribution</div>
        <p style="font-size:.88rem;color:#374151;line-height:1.8;margin-top:10px;">
        P. Cortez and A. Silva.
        <i>Using Data Mining to Predict Secondary School Student Performance.</i>
        In A. Brito and J. Teixeira Eds., Proceedings of 5th FUture BUsiness TEChnology
        Conference (FUBUTEC 2008) pp. 5-12, Porto, Portugal, April, 2008, EUROSIS,
        ISBN 978-9077381-39-7.<br><br>
        Dataset available under <b>Creative Commons Attribution 4.0 International (CC BY 4.0)</b>.<br>
        Source: <a href="https://archive.ics.uci.edu/dataset/320/student+performance">
        https://archive.ics.uci.edu/dataset/320/student+performance</a>
        </p>
    </div>
    """, unsafe_allow_html=True)
