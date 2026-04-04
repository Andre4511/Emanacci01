# =========================================================
# GLOBAL STYLES (Glass / Dark / Emanacci Look)
# =========================================================

import streamlit as st


def apply_global_styles():
    st.markdown(
        """
<style>
/* ===== Background ===== */
html, body, [data-testid="stAppViewContainer"] {
    background:
        radial-gradient(circle at 20% 20%, rgba(90, 120, 255, 0.10), transparent 25%),
        radial-gradient(circle at 80% 10%, rgba(0, 255, 220, 0.08), transparent 20%),
        linear-gradient(180deg, #05070d 0%, #070b14 40%, #03050a 100%) !important;
}

/* ===== Sidebar ===== */
section[data-testid="stSidebar"] {
    background:
        linear-gradient(180deg, rgba(10,14,24,0.85), rgba(8,12,22,0.75)) !important;
    backdrop-filter: blur(14px);
    border-right: 1px solid rgba(120, 180, 255, 0.15);
}

/* ===== Cards / Container ===== */
.em-card {
    border: 1px solid rgba(120, 180, 255, 0.18);
    border-radius: 12px;
    padding: 0.9rem 1rem;
    background: rgba(120, 180, 255, 0.04);
    box-shadow: 0 10px 28px rgba(0,0,0,0.18);
}

/* ===== Metrics ===== */
div[data-testid="stMetric"] {
    background: rgba(120, 180, 255, 0.03);
    border: 1px solid rgba(120, 180, 255, 0.14);
    border-radius: 10px !important;
    padding: 0.6rem;
}

/* ===== Buttons ===== */
.stButton > button {
    background: linear-gradient(180deg, rgba(22,28,42,0.95), rgba(13,18,30,0.95));
    border: 1px solid rgba(120, 180, 255, 0.25);
    border-radius: 8px;
    color: #e8f1ff;
    font-weight: 600;
}

.stButton > button:hover {
    border-color: rgba(120, 180, 255, 0.45);
    box-shadow: 0 0 16px rgba(120, 180, 255, 0.10);
}

/* ===== Inputs ===== */
div[data-baseweb="input"] > div,
div[data-baseweb="select"] > div {
    background: rgba(9, 13, 22, 0.82) !important;
    border: 1px solid rgba(120, 180, 255, 0.16) !important;
    border-radius: 8px !important;
}

/* ===== Charts Container ===== */
.em-chart {
    border-radius: 14px;
    padding: 0.5rem;
    border: 1px solid rgba(120, 180, 255, 0.16);
    background: rgba(120, 180, 255, 0.04);
}

/* ===== Divider ===== */
hr {
    border-top: 1px solid rgba(120, 180, 255, 0.12);
}
</style>
""",
        unsafe_allow_html=True,
    )