"""
styles.py  —  Shared CSS & HTML helpers
Light theme enforced via .streamlit/config.toml.

Icon strategy
-------------
Material Symbols Rounded (Google Fonts) are used throughout the app via
the helper function mi(name) which returns an HTML <span> element.
The font is loaded once in GLOBAL_CSS.

st.page_link(icon=) and st.set_page_config(page_icon=) only accept emoji
characters — those two call-sites retain emoji as Streamlit requires it.
All other UI icons use Material Symbols.
"""

# ── Material icon helper ───────────────────────────────────────────────────────
def mi(name: str, size: str = "20px", color: str = "inherit",
       style: str = "") -> str:
    """
    Return an HTML span rendering a Material Symbols Rounded icon.

    Usage in f-strings:
        f'<div>{mi("dashboard")} Overview</div>'

    Parameters
    ----------
    name  : Material Symbols icon name (snake_case), e.g. "check_circle"
    size  : CSS font-size, default "20px"
    color : CSS color, default "inherit"
    style : Extra inline CSS
    """
    return (
        f'<span class="material-symbols-rounded" '
        f'style="font-size:{size};color:{color};vertical-align:middle;'
        f'line-height:1;{style}">'
        f'{name}</span>'
    )


GLOBAL_CSS = """
<style>
/* ── Google Fonts: Inter + Material Symbols Rounded ── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
@import url('https://fonts.googleapis.com/css2?family=Material+Symbols+Rounded:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200');

/* Icon rendering defaults */
.material-symbols-rounded {
    font-variation-settings: 'FILL' 0, 'wght' 400, 'GRAD' 0, 'opsz' 24;
    display: inline-flex;
    align-items: center;
    user-select: none;
}
/* Filled variant */
.material-symbols-rounded.filled {
    font-variation-settings: 'FILL' 1, 'wght' 400, 'GRAD' 0, 'opsz' 24;
}

/* ── Base ── */
html, body {
    font-family: 'Inter', 'Segoe UI', system-ui, sans-serif !important;
    color: #0F172A !important;
}
[data-testid="stAppViewContainer"] { background: #F5F7FB !important; }
[data-testid="stHeader"]           { background: transparent !important; }
.block-container {
    padding: 24px 32px 48px 32px !important;
    max-width: 100% !important;
}

/* ── Main content text — always dark ── */
[data-testid="stMain"] p,
[data-testid="stMain"] span,
[data-testid="stMain"] label,
[data-testid="stMain"] small,
[data-testid="stMain"] li,
[data-testid="stMain"] h1,
[data-testid="stMain"] h2,
[data-testid="stMain"] h3 {
    color: #172033 !important;
}
[data-testid="stMain"] [data-testid="stWidgetLabel"] p {
    color: #172033 !important;
    font-weight: 600 !important;
    font-size: 0.875rem !important;
}
[data-testid="stMain"] small,
[data-testid="stMain"] [data-testid="InputInstructions"] {
    color: #64748B !important;
}

/* ── Input fields ── */
/* Scope to explicit number/text input containers only.
   The bare `input` selector must NOT be used — it matches the hidden
   <input> inside every BaseWeb <Select> combobox and produces a visible
   rectangular border artifact next to the selected value. */
[data-testid="stNumberInput"] input,
[data-testid="stTextInput"] input,
[data-testid="stTextArea"] textarea {
    background-color: #FFFFFF !important;
    color: #172033 !important;
    border: 1px solid #CBD5E1 !important;
    border-radius: 8px !important;
}
[data-testid="stNumberInput"] input:focus,
[data-testid="stTextInput"] input:focus,
[data-testid="stTextArea"] textarea:focus {
    border-color: #2563EB !important;
    box-shadow: 0 0 0 3px rgba(37,99,235,.10) !important;
    outline: none !important;
}

/* Neutralise any border/background on inputs nested inside a select.
   These are internal BaseWeb value-holder inputs — they must be invisible. */
[data-baseweb="select"] input,
[data-baseweb="select"] input:focus,
div[role="combobox"] input,
div[role="combobox"] input:focus {
    background: transparent !important;
    border: none !important;
    outline: none !important;
    box-shadow: none !important;
    padding: 0 !important;
    width: 0 !important;
    min-width: 0 !important;
}

[data-testid="stNumberInput"] button {
    background: #F8FAFC !important;
    color: #172033 !important;
    border: 1px solid #CBD5E1 !important;
}
[data-testid="stNumberInput"] button svg { fill: #334155 !important; }

/* ── Selectbox ── */
[data-baseweb="select"] > div,
div[role="combobox"] {
    background-color: #FFFFFF !important;
    color: #172033 !important;
    border: 1px solid #CBD5E1 !important;
    border-radius: 8px !important;
}
div[role="combobox"] span,
[data-baseweb="select"] span { color: #172033 !important; }
[data-baseweb="select"] svg  { fill: #475569 !important; }
[data-baseweb="popover"],
[data-baseweb="menu"],
[role="listbox"] {
    background-color: #FFFFFF !important;
    border: 1px solid #E2E8F0 !important;
    border-radius: 10px !important;
    box-shadow: 0 8px 24px rgba(0,0,0,.10) !important;
}
[data-baseweb="menu"] li,
[data-baseweb="option"],
[role="option"] { background-color: #FFFFFF !important; color: #172033 !important; }
[data-baseweb="menu"] li:hover,
[data-baseweb="option"]:hover {
    background-color: #EFF6FF !important;
    color: #1D4ED8 !important;
}

/* ── Sliders ── */
[data-testid="stSlider"] div[role="slider"] { background: #2563EB !important; }
[data-testid="stSlider"] p,
[data-testid="stSlider"] span              { color: #172033 !important; }
[data-testid="stSlider"] [data-testid="stTickBarMin"],
[data-testid="stSlider"] [data-testid="stTickBarMax"] { color: #64748B !important; }

/* ── Tabs ── */
[data-baseweb="tab-list"] {
    background: transparent !important;
    border-bottom: 2px solid #E2E8F0 !important;
    gap: 4px;
}
[data-baseweb="tab"] {
    background: transparent !important;
    color: #64748B !important;
    font-weight: 600 !important;
    font-size: 0.875rem !important;
    border: none !important;
    padding: 8px 18px !important;
}
[data-baseweb="tab"]:hover { color: #2563EB !important; }
[data-baseweb="tab"][aria-selected="true"] {
    color: #2563EB !important;
    border-bottom: 2px solid #2563EB !important;
    background: transparent !important;
}

/* ── Buttons ── */
.stButton > button,
[data-testid="stFormSubmitButton"] > button {
    background: #2563EB !important;
    color: #FFFFFF !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    font-size: 0.92rem !important;
    padding: 10px 28px !important;
    transition: background 0.18s !important;
}
.stButton > button:hover,
[data-testid="stFormSubmitButton"] > button:hover { background: #1D4ED8 !important; }

/* ── Form ── */
[data-testid="stForm"] {
    background: #FFFFFF !important;
    border: 1px solid #E2E8F0 !important;
    border-radius: 14px !important;
    padding: 4px 8px !important;
}

/* ── DataFrames ── */
[data-testid="stDataFrame"] { border-radius: 10px !important; overflow: hidden !important; }

/* ── Expander ── */
[data-testid="stExpander"] {
    background: #FFFFFF !important;
    border: 1px solid #E2E8F0 !important;
    border-radius: 10px !important;
}
[data-testid="stExpander"] summary p {
    color: #172033 !important;
    font-weight: 600 !important;
}

/* ── Download button ── */
[data-testid="stDownloadButton"] button {
    background: #F1F5F9 !important;
    color: #1E293B !important;
    border: 1px solid #CBD5E1 !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
}

/* ── Alerts ── */
[data-testid="stAlert"] p { color: inherit !important; }

/* ── Scrollbar ── */
::-webkit-scrollbar       { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: #CBD5E1; border-radius: 99px; }

/* ════════════════════════════════════════════════
   SIDEBAR
   ════════════════════════════════════════════════ */
[data-testid="stSidebar"] {
    background: #142B4A !important;
    border-right: none !important;
}
[data-testid="stSidebar"] > div:first-child { padding-top: 0 !important; }

[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] small,
[data-testid="stSidebar"] li {
    color: #A8BDD0 !important;
}

/* Sidebar collapse toggle */
[data-testid="stSidebarCollapsedControl"] { background: #142B4A !important; }
[data-testid="stSidebarCollapsedControl"] button { color: #A8BDD0 !important; }
[data-testid="stSidebarCollapsedControl"] svg    { fill: #A8BDD0 !important; }

/* Nav link pills */
[data-testid="stSidebar"] [data-testid="stPageLink-NavLink"] {
    border-radius: 8px !important;
    margin: 1px 8px !important;
    padding: 9px 12px !important;
    font-size: 0.875rem !important;
    font-weight: 500 !important;
    color: #A8BDD0 !important;
    transition: background 0.15s, color 0.15s !important;
}
[data-testid="stSidebar"] [data-testid="stPageLink-NavLink"]:hover {
    background: rgba(255,255,255,.09) !important;
    color: #FFFFFF !important;
}
[data-testid="stSidebar"] [data-testid="stPageLink-NavLink"][aria-current="page"] {
    background: rgba(37,99,235,.28) !important;
    color: #FFFFFF !important;
}
[data-testid="stSidebar"] a { text-decoration: none !important; }

/* ════════════════════════════════════════════════
   CUSTOM COMPONENT CLASSES
   ════════════════════════════════════════════════ */

/* White card */
.card {
    background: #FFFFFF;
    border-radius: 12px;
    border: 1px solid #E2E8F0;
    padding: 20px 22px;
    box-shadow: 0 1px 3px rgba(0,0,0,.05), 0 4px 12px rgba(0,0,0,.04);
    margin-bottom: 16px;
}

/* KPI card */
.kpi-card {
    background: #FFFFFF;
    border-radius: 12px;
    border: 1px solid #E2E8F0;
    padding: 18px 20px;
    box-shadow: 0 1px 3px rgba(0,0,0,.05), 0 4px 12px rgba(0,0,0,.04);
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
    min-height: 108px;
    margin-bottom: 14px;
}
.kpi-left   { flex: 1; min-width: 0; }
.kpi-label  {
    font-size: 0.70rem;
    font-weight: 700;
    color: #64748B;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-bottom: 6px;
}
.kpi-value  { font-size: 1.9rem; font-weight: 800; line-height: 1.1; margin-bottom: 5px; }
.kpi-sub    { font-size: 0.74rem; color: #64748B; font-weight: 500; line-height: 1.4; }
.kpi-icon   {
    width: 40px; height: 40px; flex-shrink: 0;
    border-radius: 10px;
    display: flex; align-items: center; justify-content: center;
    margin-left: 10px;
}
.kpi-green { color: #10B981; } .icon-green { background: #D1FAE5; }
.kpi-blue  { color: #2563EB; } .icon-blue  { background: #DBEAFE; }
.kpi-teal  { color: #0D9488; } .icon-teal  { background: #CCFBF1; }
.kpi-red   { color: #EF4444; } .icon-red   { background: #FEE2E2; }
.kpi-amber { color: #D97706; } .icon-amber { background: #FEF3C7; }
.kpi-navy  { color: #142B4A; } .icon-navy  { background: #E0E7FF; }

/* Chart headings */
.chart-title {
    font-size: 0.95rem;
    font-weight: 700;
    color: #172033;
    margin-bottom: 2px;
    display: flex;
    align-items: center;
    gap: 6px;
}
.chart-sub { font-size: 0.76rem; color: #94A3B8; margin-bottom: 10px; }

/* Page header */
.page-title {
    font-size: 1.8rem;
    font-weight: 800;
    color: #172033;
    margin: 0 0 2px 0;
    letter-spacing: -0.3px;
    display: flex;
    align-items: center;
    gap: 10px;
}
.page-sub { font-size: 0.88rem; color: #64748B; margin: 0 0 20px 0; }

/* Info / warning boxes */
.insight-box {
    background: #EFF6FF;
    border-left: 4px solid #2563EB;
    border-radius: 0 8px 8px 0;
    padding: 10px 14px;
    font-size: 0.85rem;
    color: #1E40AF;
    margin: 10px 0;
    display: flex;
    align-items: flex-start;
    gap: 8px;
}
.warn-box {
    background: #FFFBEB;
    border-left: 4px solid #D97706;
    border-radius: 0 8px 8px 0;
    padding: 10px 14px;
    font-size: 0.85rem;
    color: #78350F;
    margin: 10px 0;
    display: flex;
    align-items: flex-start;
    gap: 8px;
}

/* Form section band */
.form-section {
    background: #EFF6FF;
    border-left: 4px solid #2563EB;
    border-radius: 0 10px 10px 0;
    padding: 9px 14px;
    margin: 18px 0 10px 0;
    font-size: 0.9rem;
    font-weight: 700;
    color: #172033;
    display: flex;
    align-items: center;
    gap: 8px;
}

/* Divider */
.divider { border: none; border-top: 1px solid #E2E8F0; margin: 16px 0; }

/* Field group label */
.field-group-label {
    font-size: 0.72rem;
    font-weight: 700;
    color: #64748B;
    text-transform: uppercase;
    letter-spacing: 0.07em;
    margin: 14px 0 4px 2px;
    display: flex;
    align-items: center;
    gap: 4px;
}
</style>
"""


def inject_css():
    """Inject global CSS + Material Symbols font. Call once per page."""
    import streamlit as st
    st.markdown(GLOBAL_CSS, unsafe_allow_html=True)


def sidebar_nav():
    """
    Renders sidebar: branding → nav links → footer.
    Hides Streamlit's auto-nav and uses manual st.page_link() so branding
    appears first.  st.page_link icon= only accepts emoji — we use the
    closest semantic emoji there and Material Icons everywhere else.
    """
    import streamlit as st

    # Hide Streamlit's auto-injected pages nav (always renders above sidebar content)
    st.markdown("""
    <style>
    [data-testid="stSidebarNav"] { display: none !important; }
    </style>
    """, unsafe_allow_html=True)

    with st.sidebar:
        # 1. BRANDING ──────────────────────────────────────────────────────
        st.markdown("""
        <div style="padding:20px 16px 16px 16px;
                    border-bottom:1px solid rgba(255,255,255,.10);
                    margin-bottom:6px;">
            <div style="display:flex;align-items:center;gap:10px;">
                <div style="background:#2563EB;border-radius:10px;
                            width:36px;height:36px;flex-shrink:0;
                            display:flex;align-items:center;justify-content:center;">
                    <span class="material-symbols-rounded filled"
                          style="font-size:20px;color:#FFFFFF;
                                 font-variation-settings:'FILL' 1,'wght' 400,'GRAD' 0,'opsz' 24;">
                        school
                    </span>
                </div>
                <div>
                    <div style="font-size:0.92rem;font-weight:800;
                                color:#FFFFFF;line-height:1.2;">
                        Student Analytics
                    </div>
                    <div style="font-size:0.70rem;color:#4E6A88;margin-top:2px;">
                        Education Dashboard
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # 2. NAVIGATION ────────────────────────────────────────────────────
        # Inject CSS that prepends Material Symbols icons before each nav link
        # using ::before pseudo-elements and nth-child selectors.
        # Material Symbols Rounded uses the icon ligature name as the content.
        st.markdown("""
        <style>
        /* Shared icon style for all nav links */
        [data-testid="stSidebar"] [data-testid="stPageLink-NavLink"]::before {
            font-family: 'Material Symbols Rounded';
            font-variation-settings: 'FILL' 0, 'wght' 300, 'GRAD' 0, 'opsz' 24;
            font-size: 18px;
            color: #A8BDD0;
            margin-right: 8px;
            vertical-align: middle;
            line-height: 1;
            display: inline-block;
        }
        [data-testid="stSidebar"] [data-testid="stPageLink-NavLink"][aria-current="page"]::before {
            color: #FFFFFF;
        }
        /* Per-link icons via nth-of-type on the wrapping div */
        [data-testid="stSidebar"] [data-testid="stPageLink"]:nth-of-type(1) [data-testid="stPageLink-NavLink"]::before { content: 'dashboard'; }
        [data-testid="stSidebar"] [data-testid="stPageLink"]:nth-of-type(2) [data-testid="stPageLink-NavLink"]::before { content: 'dataset'; }
        [data-testid="stSidebar"] [data-testid="stPageLink"]:nth-of-type(3) [data-testid="stPageLink-NavLink"]::before { content: 'psychology'; }
        [data-testid="stSidebar"] [data-testid="stPageLink"]:nth-of-type(4) [data-testid="stPageLink-NavLink"]::before { content: 'compare_arrows'; }
        [data-testid="stSidebar"] [data-testid="stPageLink"]:nth-of-type(5) [data-testid="stPageLink-NavLink"]::before { content: 'insights'; }
        [data-testid="stSidebar"] [data-testid="stPageLink"]:nth-of-type(6) [data-testid="stPageLink-NavLink"]::before { content: 'info'; }
        </style>
        """, unsafe_allow_html=True)

        nav_items = [
            ("app.py",                            "Overview"),
            ("pages/2_Dataset_Explorer.py",       "Dataset Explorer"),
            ("pages/3_Performance_Prediction.py", "Performance Prediction"),
            ("pages/4_Model_Comparison.py",       "Model Comparison"),
            ("pages/5_Academic_Insights.py",      "Insights"),
            ("pages/6_About.py",                  "About"),
        ]
        for page_path, label in nav_items:
            st.page_link(page_path, label=label)

        # 3. FOOTER ────────────────────────────────────────────────────────
        st.markdown("""
        <div style="margin-top:28px;padding:12px 16px;
                    border-top:1px solid rgba(255,255,255,.10);">
            <div style="font-size:0.68rem;color:#4E6A88;line-height:1.8;">
                UCI Student Performance<br>
                Cortez &amp; Silva, 2008<br>
                CC BY 4.0
            </div>
        </div>
        """, unsafe_allow_html=True)


def kpi_card(label: str, value: str, sub: str, icon_name: str,
             icon_class: str = "icon-blue", value_class: str = "kpi-blue",
             filled: bool = True) -> str:
    """
    Return HTML for a KPI card using a Material Symbols icon.

    Parameters
    ----------
    label      : Card label (uppercase)
    value      : Primary metric value
    sub        : Secondary descriptive text
    icon_name  : Material Symbols icon name, e.g. "check_circle"
    icon_class : CSS class for icon background colour, e.g. "icon-green"
    value_class: CSS class for value colour, e.g. "kpi-green"
    filled     : Whether to use the filled icon variant
    """
    fill_val = "1" if filled else "0"
    return f"""
    <div class="kpi-card">
        <div class="kpi-left">
            <div class="kpi-label">{label}</div>
            <div class="kpi-value {value_class}">{value}</div>
            <div class="kpi-sub">{sub}</div>
        </div>
        <div class="kpi-icon {icon_class}">
            <span class="material-symbols-rounded"
                  style="font-size:22px;
                         font-variation-settings:'FILL' {fill_val},'wght' 400,'GRAD' 0,'opsz' 24;">
                {icon_name}
            </span>
        </div>
    </div>"""


def page_header(title: str, subtitle: str = "", icon: str = ""):
    """Render a page title with optional Material Icon and subtitle."""
    import streamlit as st
    icon_html = (
        f'<span class="material-symbols-rounded" '
        f'style="font-size:1.8rem;color:#2563EB;vertical-align:middle;">'
        f'{icon}</span> '
    ) if icon else ""
    st.markdown(f"""
    <div style="margin-bottom:18px;">
        <div class="page-title">{icon_html}{title}</div>
        {"" if not subtitle else f'<div class="page-sub">{subtitle}</div>'}
    </div>
    """, unsafe_allow_html=True)


def section_header(icon: str, title: str) -> str:
    """Return HTML for a form section header with a Material Icon."""
    return (
        f'<div class="form-section">'
        f'<span class="material-symbols-rounded" '
        f'style="font-size:18px;color:#2563EB;flex-shrink:0;">{icon}</span>'
        f'{title}</div>'
    )
