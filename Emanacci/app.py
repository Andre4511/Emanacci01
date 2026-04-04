import streamlit as st

from components.navigation import (
    ensure_navigation_state,
    render_sidebar_navigation,
)
from pages.dashboard import render_dashboard
from pages.analyse import render_analyse_page
from pages.placeholders import (
    render_paper_trading_placeholder,
    render_journal_placeholder,
    render_backtest_placeholder,
    render_settings_placeholder,
)
from components.styles import apply_global_styles
from pages.paper_trading import render_paper_trading_page
from pages.journal import render_journal_page

# =========================================================
# SESSION STATE DEFAULTS
# Nur die Werte, die wir aktuell wirklich brauchen.
# =========================================================
if "period" not in st.session_state:
    st.session_state.period = "6mo"

if "interval" not in st.session_state:
    st.session_state.interval = "1d"

if "ticker" not in st.session_state:
    st.session_state.ticker = "TSLA"

if "watchlist" not in st.session_state:
    st.session_state.watchlist = ["TSLA", "AAPL", "NVDA"]


# =========================================================
# BASIS LAYOUT
# =========================================================
st.set_page_config(
    page_title="Emanacci",
    page_icon="📈",
    layout="wide",
)

st.markdown(
    """
    <style>
    .main .block-container {
        padding-top: 1rem;
        padding-bottom: 2rem;
        max-width: 1400px;
    }

    div[data-testid="stMetric"] {
        border: 1px solid rgba(120, 180, 255, 0.12);
        border-radius: 12px;
        padding: 0.35rem 0.5rem;
        background: rgba(120, 180, 255, 0.03);
    }

    div[data-testid="stVerticalBlock"] div[data-testid="stPlotlyChart"] {
        border-radius: 14px;
        overflow: hidden;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

apply_global_styles()

# =========================================================
# NAVIGATION
# =========================================================
ensure_navigation_state()
active_page = render_sidebar_navigation()


# =========================================================
# ROUTER
# Tabs sind weg. Jede Seite läuft jetzt separat.
# =========================================================
if active_page == "dashboard":
    render_dashboard()
    st.stop()

if active_page == "analyse":
    render_analyse_page()
    st.stop()

if active_page == "paper_trading":
    render_paper_trading_page()
    st.stop()

if active_page == "journal":
    render_journal_page()
    st.stop()

if active_page == "backtest":
    render_backtest_placeholder()
    st.stop()

if active_page == "settings":
    render_settings_placeholder()
    st.stop()


# =========================================================
# FALLBACK
# =========================================================
render_dashboard()
