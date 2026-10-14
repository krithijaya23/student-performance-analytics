"""
3_Performance_Prediction.py  —  Performance Prediction
Single-column layout: settings → form → result (always at bottom).
Result rendered with native Streamlit components — no raw HTML blobs.
Auto-scroll to result via JS after submit. All ML logic unchanged.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import streamlit as st
import pandas as pd

from src.data_loader  import load_uci_dataset
from src.train_models import train_all_models, get_best_model
from src.predictions  import predict_grade
from src.evaluation   import interpretation
from src.styles       import inject_css, sidebar_nav, section_header, mi

st.set_page_config(page_title="Grade Prediction", page_icon="🔮", layout="wide")
inject_css()
sidebar_nav()

# ── Page-specific CSS ──────────────────────────────────────────────────────────
st.markdown("""
<style>
/* Section jump nav */
.section-nav {
    display: flex;
    gap: 8px;
    flex-wrap: wrap;
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 10px;
    padding: 10px 14px;
    margin-bottom: 20px;
    box-shadow: 0 1px 3px rgba(0,0,0,.04);
}
.section-nav a {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    padding: 5px 12px;
    border-radius: 6px;
    font-size: 0.80rem;
    font-weight: 600;
    color: #475569;
    text-decoration: none !important;
    background: #F8FAFC;
    border: 1px solid #E2E8F0;
    transition: background 0.15s, color 0.15s;
    white-space: nowrap;
}
.section-nav a:hover { background: #EFF6FF; color: #2563EB; border-color: #BFDBFE; }

/* Invisible scroll target — sits 72 px above the visible element */
.scroll-anchor {
    display: block;
    position: relative;
    top: -72px;
    visibility: hidden;
    pointer-events: none;
}

/* Field group label */
.field-group-label {
    font-size: 0.72rem;
    font-weight: 700;
    color: #64748B;
    text-transform: uppercase;
    letter-spacing: 0.07em;
    margin: 14px 0 4px 2px;
}

/* Submit button */
[data-testid="stFormSubmitButton"] > button {
    height: 48px !important;
    font-size: 1rem !important;
}

/* Result section card */
.result-score-card {
    border-radius: 14px;
    padding: 28px 24px 22px 24px;
    text-align: center;
    margin-bottom: 4px;
}
.result-grade-num {
    font-size: 4rem;
    font-weight: 900;
    line-height: 1;
    letter-spacing: -2px;
}
.result-grade-denom {
    font-size: 1rem;
    margin-top: 4px;
    opacity: 0.7;
}
.result-badge {
    display: inline-block;
    border-radius: 20px;
    padding: 4px 22px;
    font-size: .84rem;
    font-weight: 700;
    margin-top: 12px;
    border: 1.5px solid;
}
.result-model-meta {
    font-size: .74rem;
    margin-top: 10px;
    opacity: 0.6;
}

/* Grade scale bar */
.grade-scale-bar {
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 10px;
    padding: 12px 16px;
}
.gsb-track {
    background: #F1F5F9;
    border-radius: 99px;
    height: 10px;
    margin: 6px 0 3px 0;
    overflow: hidden;
}
.gsb-fill { height: 100%; border-radius: 99px; }
.gsb-labels {
    display: flex;
    justify-content: space-between;
    font-size: .68rem;
    color: #94A3B8;
}

/* Grade chips */
.grade-chips { display: flex; gap: 6px; margin-top: 2px; }
.grade-chip {
    flex: 1; border-radius: 8px; padding: 8px 6px;
    text-align: center; min-width: 56px;
}
.grade-chip-val { font-size: .9rem; font-weight: 800; }
.grade-chip-lbl { font-size: .64rem; margin-top: 2px; }

/* Back to top */
.back-to-top {
    display: inline-flex; align-items: center; gap: 5px;
    font-size: .78rem; font-weight: 600; color: #64748B;
    text-decoration: none !important;
    padding: 5px 12px; border: 1px solid #E2E8F0;
    border-radius: 8px; background: #F8FAFC;
}
.back-to-top:hover { color: #2563EB; background: #EFF6FF; }
</style>
""", unsafe_allow_html=True)


# ── Helpers ────────────────────────────────────────────────────────────────────
def section(icon_name: str, title: str, anchor_id: str = ""):
    anchor_html = (
        f'<span class="scroll-anchor" id="{anchor_id}"></span>' if anchor_id else ""
    )
    st.markdown(anchor_html + section_header(icon_name, title), unsafe_allow_html=True)


# ── Page header ────────────────────────────────────────────────────────────────
st.markdown(f"""
<span class="scroll-anchor" id="page-top"></span>
<div style="margin-bottom:16px;">
    <div class="page-title">
        {mi("psychology","1.8rem","#2563EB")} Student Grade Predictor
    </div>
    <div class="page-sub">
        Enter a student's academic and personal information to estimate
        their final grade on a scale of 0–20.
    </div>
</div>
""", unsafe_allow_html=True)

# ── Load models ────────────────────────────────────────────────────────────────
@st.cache_resource(show_spinner=False)
def load_models():
    m = {}
    for subject in ["Mathematics", "Portuguese"]:
        df, _ = load_uci_dataset(subject)
        if df is not None:
            label = "math" if subject == "Mathematics" else "por"
            res, _, _ = train_all_models(df, label)
            m[subject] = {"results": res, "df": df}
    return m

with st.spinner("Loading models…"):
    model_map = load_models()

if not model_map:
    st.error("No datasets loaded. Check the data/ folder.")
    st.stop()

# ── Prediction settings strip ──────────────────────────────────────────────────
cfg1, cfg2, cfg3 = st.columns([1.5, 2, 2.5], gap="medium")

with cfg1:
    subject = st.selectbox(
        "Subject", list(model_map.keys()),
        help="Choose the subject you want to predict grades for.",
    )

results      = model_map[subject]["results"]
ref_df       = model_map[subject]["df"]
trained      = {k: v for k, v in results.items() if v["status"] == "trained"}
default_best = get_best_model(results)
opts         = list(trained.keys())

with cfg2:
    sel_model = st.selectbox(
        "Prediction model", opts,
        index=opts.index(default_best) if default_best in opts else 0,
        help="Random Forest and Gradient Boosting usually perform best.",
    )

pipeline = trained[sel_model]["pipeline"]
test_m   = trained[sel_model]["test_metrics"]

with cfg3:
    st.markdown(f"""
    <div style="background:#F0F9FF;border:1px solid #BAE6FD;border-radius:10px;
                padding:10px 16px;font-size:.84rem;color:#0369A1;line-height:1.75;">
        <b>Model performance</b> &nbsp;&nbsp;
        MAE <b>{test_m['MAE']}</b> &nbsp;·&nbsp;
        RMSE <b>{test_m['RMSE']}</b> &nbsp;·&nbsp;
        R² <b>{test_m['R2']}</b>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)

# ── Section jump nav ───────────────────────────────────────────────────────────
st.markdown("""
<nav class="section-nav" aria-label="Jump to section">
    <span style="font-size:.74rem;font-weight:700;color:#94A3B8;
                 align-self:center;margin-right:4px;white-space:nowrap;">
        Jump to:
    </span>
    <a href="#sec-basic">
        <span class="material-symbols-rounded" style="font-size:15px;">person</span>
        Basic Info
    </a>
    <a href="#sec-family">
        <span class="material-symbols-rounded" style="font-size:15px;">family_restroom</span>
        Family
    </a>
    <a href="#sec-school">
        <span class="material-symbols-rounded" style="font-size:15px;">school</span>
        School &amp; Study
    </a>
    <a href="#sec-lifestyle">
        <span class="material-symbols-rounded" style="font-size:15px;">groups</span>
        Lifestyle
    </a>
    <a href="#sec-result">
        <span class="material-symbols-rounded" style="font-size:15px;">query_stats</span>
        Result
    </a>
</nav>
""", unsafe_allow_html=True)

# ── Option maps (must stay compatible with trained pipeline) ───────────────────
SCHOOL_MAP  = {"GP": "Gabriel Pereira (GP)",  "MS": "Mousinho da Silveira (MS)"}
SEX_MAP     = {"F": "Female",                  "M": "Male"}
ADDR_MAP    = {"U": "Urban",                   "R": "Rural"}
FAMSIZE_MAP = {"LE3": "≤ 3 members",          "GT3": "> 3 members"}
PSTAT_MAP   = {"T": "Living together",         "A": "Living apart"}
EDU_MAP     = {
    0: "None",
    1: "Primary (up to 4th grade)",
    2: "Middle school (5th–9th grade)",
    3: "Secondary school",
    4: "Higher education",
}
JOB_MAP = {
    "teacher":  "Teacher",
    "health":   "Healthcare",
    "services": "Civil services",
    "at_home":  "At home",
    "other":    "Other",
}
REASON_MAP   = {"home": "Close to home", "reputation": "School reputation",
                "course": "Course preference", "other": "Other"}
GUARDIAN_MAP = {"mother": "Mother", "father": "Father", "other": "Other"}
TRAVEL_MAP   = {1: "< 15 min", 2: "15–30 min", 3: "30 min–1 hr", 4: "Over 1 hr"}
STUDY_MAP    = {1: "< 2 hrs/week", 2: "2–5 hrs/week",
                3: "5–10 hrs/week", 4: "> 10 hrs/week"}
YESNO_MAP    = {"yes": "Yes", "no": "No"}
SCALE5_MAP   = {1: "1 — Very low",  2: "2 — Low",    3: "3 — Medium",
                4: "4 — High",      5: "5 — Very high"}
HEALTH_MAP   = {1: "1 — Very bad",  2: "2 — Bad",    3: "3 — Fair",
                4: "4 — Good",      5: "5 — Very good"}
FAMREL_MAP   = {1: "1 — Very bad",  2: "2 — Bad",    3: "3 — OK",
                4: "4 — Good",      5: "5 — Excellent"}


def sel(col: str, label: str, option_map: dict,
        default=None, help_text: str = ""):
    raw_vals     = sorted(ref_df[col].dropna().unique().tolist())
    disp_vals    = [option_map.get(str(v), str(v)) for v in raw_vals]
    rev_map      = {option_map.get(str(v), str(v)): v for v in raw_vals}
    default_disp = option_map.get(str(default)) if default is not None else None
    idx          = disp_vals.index(default_disp) if default_disp in disp_vals else 0
    return rev_map[st.selectbox(label, disp_vals, index=idx, help=help_text)]


def edu_select(label: str, help_text: str = "", default_idx: int = 2):
    options = list(EDU_MAP.values())
    chosen  = st.selectbox(label, options, index=default_idx, help=help_text)
    return [k for k, v in EDU_MAP.items() if v == chosen][0]


def slider5(label: str, scale_map: dict = SCALE5_MAP,
            default: int = 3, help_text: str = "") -> int:
    options = list(scale_map.values())
    chosen  = st.select_slider(label, options=options,
                               value=scale_map[default], help=help_text)
    return {v: k for k, v in scale_map.items()}[chosen]


# ══════════════════════════════════════════════════════════════════════════════
# PREDICTION FORM  (single column, full width)
# ══════════════════════════════════════════════════════════════════════════════
with st.form("prediction_form", clear_on_submit=False):

    # ── A: Basic Student Information ──────────────────────────────────────
    section("person", "Basic Student Information", "sec-basic")

    c1, c2, c3 = st.columns(3, gap="medium")
    with c1:
        school = sel("school", "School", SCHOOL_MAP, default="GP",
                     help_text="GP = Gabriel Pereira · MS = Mousinho da Silveira")
    with c2:
        sex = sel("sex", "Sex", SEX_MAP)
    with c3:
        address = sel("address", "Home area", ADDR_MAP,
                      help_text="Urban = city or town · Rural = countryside")

    c4, c5 = st.columns([1, 2], gap="medium")
    with c4:
        age = st.number_input("Age (years)", min_value=15, max_value=22, value=17,
                              step=1,
                              help="Students in this dataset are typically 15–18.")
    with c5:
        reason = sel("reason", "Main reason for choosing this school", REASON_MAP,
                     help_text="Course preference = specific subject offered · "
                               "Reputation = school's academic standing")

    # ── B: Family Background ──────────────────────────────────────────────
    section("family_restroom", "Family Background", "sec-family")

    c6, c7, c8 = st.columns(3, gap="medium")
    with c6:
        famsize = sel("famsize", "Family size", FAMSIZE_MAP,
                      help_text="How many people live in the student's household?")
    with c7:
        Pstatus = sel("Pstatus", "Parents' cohabitation", PSTAT_MAP,
                      help_text="Are the student's parents currently living together?")
    with c8:
        guardian = sel("guardian", "Guardian", GUARDIAN_MAP,
                       help_text="The main person responsible for the student.")

    c9, c10 = st.columns(2, gap="medium")
    with c9:
        Medu = edu_select("Mother's education level",
                          help_text="Highest qualification completed by the mother.",
                          default_idx=2)
    with c10:
        Fedu = edu_select("Father's education level",
                          help_text="Highest qualification completed by the father.",
                          default_idx=2)

    c11, c12 = st.columns(2, gap="medium")
    with c11:
        Mjob = sel("Mjob", "Mother's occupation", JOB_MAP,
                   help_text="What does the student's mother do for work?")
    with c12:
        Fjob = sel("Fjob", "Father's occupation", JOB_MAP,
                   help_text="What does the student's father do for work?")

    c13, c14 = st.columns(2, gap="medium")
    with c13:
        famrel = slider5("Quality of family relationships",
                         scale_map=FAMREL_MAP, default=4,
                         help_text="1 = very poor · 5 = excellent.")
    with c14:
        famsup = sel("famsup", "Family educational support", YESNO_MAP,
                     help_text="Helping with homework or funding private tutors.")

    # ── C: School & Study Habits ──────────────────────────────────────────
    section("school", "School & Study Habits", "sec-school")

    c15, c16 = st.columns(2, gap="medium")
    with c15:
        traveltime_disp = st.selectbox(
            "Daily travel time to school", list(TRAVEL_MAP.values()), index=0,
            help="How long does it take the student to commute to school?",
        )
        traveltime = [k for k, v in TRAVEL_MAP.items() if v == traveltime_disp][0]
    with c16:
        studytime_disp = st.selectbox(
            "Weekly study time", list(STUDY_MAP.values()), index=1,
            help="Total hours spent studying outside of class per week.",
        )
        studytime = [k for k, v in STUDY_MAP.items() if v == studytime_disp][0]

    c17, c18 = st.columns(2, gap="medium")
    with c17:
        failures = st.number_input(
            "Past class failures", min_value=0, max_value=4, value=0, step=1,
            help="0 = never failed · 4 = failed 4 or more times.",
        )
    with c18:
        absences = st.number_input(
            "School absences this year", min_value=0, max_value=93, value=4, step=1,
            help="Total school days missed. Dataset average ≈ 5–6 days.",
        )

    c19, c20, c21 = st.columns(3, gap="medium")
    with c19:
        schoolsup = sel("schoolsup", "School extra support", YESNO_MAP,
                        help_text="Extra tutoring or remedial help from school.")
    with c20:
        paid = sel("paid", "Extra paid classes", YESNO_MAP,
                   help_text="Private paid tutoring outside school hours.")
    with c21:
        higher = sel("higher", "Plans for higher education", YESNO_MAP,
                     help_text="Does the student intend to go to university?")

    c22, c23 = st.columns(2, gap="medium")
    with c22:
        nursery = sel("nursery", "Attended nursery school", YESNO_MAP,
                      help_text="Did the student attend pre-school?")
    with c23:
        activities = sel("activities", "Extracurricular activities", YESNO_MAP,
                         help_text="Sports, clubs, music, arts, etc.")

    # ── D: Lifestyle & Social Factors ─────────────────────────────────────
    section("groups", "Lifestyle & Social Factors", "sec-lifestyle")

    c24, c25 = st.columns(2, gap="medium")
    with c24:
        internet = sel("internet", "Internet access at home", YESNO_MAP,
                       help_text="Does the student have internet access for studying?")
    with c25:
        romantic = sel("romantic", "In a romantic relationship", YESNO_MAP)

    freetime = slider5(
        "Free time after school  (1 = very little · 5 = a lot)",
        help_text="How much free time the student has on a typical school day.",
    )
    goout = slider5(
        "Going out with friends  (1 = rarely · 5 = very often)",
        help_text="How frequently the student socialises outside the home.",
    )

    st.markdown('<div class="field-group-label">Alcohol consumption</div>',
                unsafe_allow_html=True)
    c26, c27 = st.columns(2, gap="medium")
    with c26:
        Walc = slider5("Weekends  (1 = very low · 5 = very high)",
                       help_text="Alcohol consumed on weekends.")
    with c27:
        Dalc = slider5("Weekdays  (1 = very low · 5 = very high)",
                       help_text="Alcohol consumed on school days.")

    health = slider5(
        "Current health status  (1 = very bad · 5 = very good)",
        scale_map=HEALTH_MAP, default=3,
        help_text="The student's overall physical health.",
    )

    st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
    submitted = st.form_submit_button("Estimate Final Grade", width="stretch")

    # Back-to-top link inside the form footer
    st.markdown("""
    <div style="text-align:center;margin-top:8px;">
        <a href="#page-top" class="back-to-top">
            <span class="material-symbols-rounded"
                  style="font-size:14px;vertical-align:middle;">arrow_upward</span>
            Back to top
        </a>
    </div>
    """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# STORE RESULT IN SESSION STATE
# ══════════════════════════════════════════════════════════════════════════════
if submitted:
    input_data = dict(
        school=school, sex=sex, age=age, address=address, famsize=famsize,
        Pstatus=Pstatus, Medu=Medu, Fedu=Fedu, Mjob=Mjob, Fjob=Fjob,
        reason=reason, guardian=guardian, traveltime=traveltime,
        studytime=studytime, failures=failures, schoolsup=schoolsup,
        famsup=famsup, paid=paid, activities=activities, nursery=nursery,
        higher=higher, internet=internet, romantic=romantic,
        famrel=famrel, freetime=freetime, goout=goout,
        Dalc=Dalc, Walc=Walc, health=health, absences=absences,
    )
    try:
        pred  = predict_grade(pipeline, input_data)
        interp = interpretation(pred)
        st.session_state["pred_result"] = {
            "pred": pred, "interp": interp,
            "model": sel_model, "subject": subject,
            "mae": test_m["MAE"], "rmse": test_m["RMSE"], "r2": test_m["R2"],
        }
    except Exception as e:
        st.session_state["pred_result"] = {"error": str(e)}

    # Signal that we should scroll after this rerun
    st.session_state["_scroll_to_result"] = True


# ══════════════════════════════════════════════════════════════════════════════
# RESULT SECTION — rendered with native Streamlit components
# ══════════════════════════════════════════════════════════════════════════════
if "pred_result" in st.session_state:
    r = st.session_state["pred_result"]

    # Scroll anchor — injected unconditionally so the JS target always exists
    st.markdown('<span class="scroll-anchor" id="sec-result"></span>',
                unsafe_allow_html=True)

    st.markdown(section_header("query_stats", "Prediction Result"),
                unsafe_allow_html=True)

    if "error" in r:
        st.error(f"Prediction failed: {r['error']}")
    else:
        pred    = r["pred"]
        interp  = r["interp"]
        model_  = r["model"]
        subj_   = r["subject"]

        # Grade band
        if pred >= 16:
            grade_label = "Excellent"
            card_bg     = "#142B4A"
            num_color   = "#10B981"
            badge_bg    = "rgba(16,185,129,.15)"
            badge_border= "#10B981"
            bar_color   = "#10B981"
        elif pred >= 14:
            grade_label = "Good"
            card_bg     = "#142B4A"
            num_color   = "#60A5FA"
            badge_bg    = "rgba(96,165,250,.15)"
            badge_border= "#60A5FA"
            bar_color   = "#2563EB"
        elif pred >= 10:
            grade_label = "Sufficient"
            card_bg     = "#142B4A"
            num_color   = "#FCD34D"
            badge_bg    = "rgba(252,211,77,.15)"
            badge_border= "#FCD34D"
            bar_color   = "#D97706"
        else:
            grade_label = "Needs Support"
            card_bg     = "#142B4A"
            num_color   = "#F87171"
            badge_bg    = "rgba(248,113,113,.15)"
            badge_border= "#F87171"
            bar_color   = "#EF4444"

        bar_pct = round((pred / 20) * 100, 1)

        # ── Score card (dark gradient header) ─────────────────────────────
        st.markdown(f"""
        <div class="result-score-card"
             style="background:linear-gradient(135deg,{card_bg} 0%,#1a3a6a 100%);
                    box-shadow:0 8px 32px rgba(20,43,74,.22);">
            <div style="font-size:.68rem;letter-spacing:.14em;text-transform:uppercase;
                        color:#94A3B8;margin-bottom:10px;">
                Estimated Final Grade (G3)
            </div>
            <div class="result-grade-num" style="color:{num_color};">{pred:.1f}</div>
            <div class="result-grade-denom" style="color:#94A3B8;">out of 20</div>
            <div class="result-badge"
                 style="background:{badge_bg};color:{num_color};
                        border-color:{badge_border};">
                {grade_label}
            </div>
            <div class="result-model-meta" style="color:#64748B;">
                {model_} &nbsp;·&nbsp; {subj_}
            </div>
        </div>
        """, unsafe_allow_html=True)

        # ── Metrics row ────────────────────────────────────────────────────
        mc1, mc2, mc3 = st.columns(3, gap="small")
        mc1.metric("Predicted Grade", f"{pred:.1f} / 20")
        mc2.metric("Avg Model Error", f"± {r['mae']} pts")
        mc3.metric("Variance Explained", f"R² {r['r2']}")

        st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)

        # ── Progress bar ───────────────────────────────────────────────────
        st.markdown(f"""
        <div class="grade-scale-bar">
            <div style="display:flex;justify-content:space-between;
                        font-size:.75rem;font-weight:700;color:#475569;">
                <span>Grade progress</span>
                <span style="color:{num_color};">{pred:.1f} / 20 &nbsp;({bar_pct}%)</span>
            </div>
            <div class="gsb-track">
                <div class="gsb-fill"
                     style="width:{bar_pct}%;background:{bar_color};"></div>
            </div>
            <div class="gsb-labels"><span>0</span><span>10</span><span>20</span></div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)

        # ── Two-column: interpretation + grade scale ───────────────────────
        ic1, ic2 = st.columns([3, 2], gap="medium")

        with ic1:
            st.markdown(f"""
            <div class="insight-box" style="font-size:.88rem;align-items:flex-start;">
                <span class="material-symbols-rounded"
                      style="font-size:18px;color:#2563EB;flex-shrink:0;margin-top:1px;
                             font-variation-settings:'FILL' 1,'wght' 400,'GRAD' 0,'opsz' 24;">
                    info
                </span>
                <span>{interp}</span>
            </div>
            """, unsafe_allow_html=True)

        with ic2:
            st.markdown("""
            <div class="card" style="padding:12px 14px;">
                <div style="font-size:.68rem;font-weight:700;color:#64748B;
                            text-transform:uppercase;letter-spacing:.07em;
                            margin-bottom:8px;">
                    Grading scale (0–20)
                </div>
                <div class="grade-chips">
                    <div class="grade-chip" style="background:#D1FAE5;">
                        <div class="grade-chip-val" style="color:#065F46;">16–20</div>
                        <div class="grade-chip-lbl" style="color:#065F46;">Excellent</div>
                    </div>
                    <div class="grade-chip" style="background:#DBEAFE;">
                        <div class="grade-chip-val" style="color:#1E40AF;">14–15</div>
                        <div class="grade-chip-lbl" style="color:#1E40AF;">Good</div>
                    </div>
                    <div class="grade-chip" style="background:#FEF3C7;">
                        <div class="grade-chip-val" style="color:#92400E;">10–13</div>
                        <div class="grade-chip-lbl" style="color:#92400E;">Sufficient</div>
                    </div>
                    <div class="grade-chip" style="background:#FEE2E2;">
                        <div class="grade-chip-val" style="color:#991B1B;">0–9</div>
                        <div class="grade-chip-lbl" style="color:#991B1B;">Support</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        # ── Disclaimer ─────────────────────────────────────────────────────
        st.markdown("""
        <div class="warn-box" style="font-size:.80rem;margin-top:4px;">
            <span class="material-symbols-rounded"
                  style="font-size:16px;flex-shrink:0;color:#D97706;
                         font-variation-settings:'FILL' 1,'wght' 400,'GRAD' 0,'opsz' 24;">
                warning
            </span>
            <span>Statistical estimate only — not a guaranteed outcome.
            Use for educational exploration, not high-stakes decisions.</span>
        </div>
        """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# AUTO-SCROLL  — fires once after a successful prediction submit
# Uses st.components.v1.html so the script executes in Streamlit's iframe
# context. The flag is cleared immediately to prevent re-firing on reruns.
# ══════════════════════════════════════════════════════════════════════════════
if st.session_state.pop("_scroll_to_result", False):
    import streamlit.components.v1 as components
    components.html("""
    <script>
    // Walk up to the parent Streamlit document and scroll to #sec-result
    (function () {
        var prefersReduced =
            window.matchMedia('(prefers-reduced-motion: reduce)').matches;

        function scroll() {
            // The anchor lives in the parent frame, not this iframe
            var doc = window.parent.document;
            var el  = doc.getElementById('sec-result');
            if (el) {
                el.scrollIntoView({
                    behavior: prefersReduced ? 'auto' : 'smooth',
                    block: 'start'
                });
            }
        }
        // Small delay so Streamlit has finished painting the result
        setTimeout(scroll, 300);
    })();
    </script>
    """, height=0)
