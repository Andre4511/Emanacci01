import streamlit as st

from components.styles import apply_global_style
from pages.dashboard import render_dashboard
from pages.analyse import render_analyse_page
from pages.paper_trading import render_paper_trading_page
from pages.journal import render_journal_page


# =========================================================
# PAGE CONFIG
# =========================================================
st.set_page_config(
    page_title="Emanacci",
    page_icon="📈",
    layout="wide",
)


# =========================================================
# SESSION STATE DEFAULTS
# =========================================================
if "period" not in st.session_state:
    st.session_state.period = "6mo"

if "interval" not in st.session_state:
    st.session_state.interval = "1d"

if "ticker" not in st.session_state:
    st.session_state.ticker = "TSLA"

if "watchlist" not in st.session_state:
    st.session_state.watchlist = ["TSLA", "AAPL", "NVDA"]

if "active_page" not in st.session_state:
    st.session_state.active_page = "dashboard"


# =========================================================
# GLOBAL CSS
# =========================================================
st.markdown(
    """
    <style>
    .main .block-container {
        padding-top: 1rem;
        padding-bottom: 7rem;
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

    .bottom-nav-wrap {
        position: fixed;
        left: 0;
        right: 0;
        bottom: 0;
        z-index: 999;
        padding: 0.5rem 0.75rem 1rem 0.75rem;
        background: linear-gradient(
            to top,
            rgba(7, 10, 18, 0.98),
            rgba(7, 10, 18, 0.88)
        );
        backdrop-filter: blur(12px);
        border-top: 1px solid rgba(255, 255, 255, 0.08);
    }

    .bottom-nav-spacer {
        height: 88px;
    }

    @media (max-width: 768px) {
        .main .block-container {
            padding-bottom: 8rem;
        }
    }

    .active-nav button {
        background: linear-gradient(135deg, #3b82f6, #60a5fa) !important;
        color: white !important;
        border: none !important;
        box-shadow: 0 0 12px rgba(59,130,246,0.6);
    }

    .inactive-nav button {
        opacity: 0.6;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

apply_global_style()


# =========================================================
# PAGE ROUTER
# =========================================================
if st.session_state.active_page == "dashboard":
    render_dashboard()

elif st.session_state.active_page == "analyse":
    render_analyse_page()

elif st.session_state.active_page == "paper_trading":
    render_paper_trading_page()

elif st.session_state.active_page == "journal":
    render_journal_page()

else:
    st.session_state.active_page = "dashboard"
    render_dashboard()

# =========================================================
# STICKY BOTTOM NAV
# =========================================================
st.markdown("###")

nav1, nav2, nav3, nav4 = st.columns(4)

with nav1:
    if st.button(
        "🏠",
        key="nav_dashboard",
        help="Dashboard",
        use_container_width=True,
        type="primary" if st.session_state.active_page == "dashboard" else "secondary",
    ):
        st.session_state.active_page = "dashboard"
        st.rerun()
    st.caption("Start")

with nav2:
    if st.button(
        "📊",
        key="nav_analyse",
        help="Analyse",
        use_container_width=True,
        type="primary" if st.session_state.active_page == "analyse" else "secondary",
    ):
        st.session_state.active_page = "analyse"
        st.rerun()
    st.caption("Analyse")

with nav3:
    if st.button(
        "💼",
        key="nav_paper_trading",
        help="Trading",
        use_container_width=True,
        type="primary" if st.session_state.active_page == "paper_trading" else "secondary",
    ):
        st.session_state.active_page = "paper_trading"
        st.rerun()
    st.caption("Trading")

with nav4:
    if st.button(
        "📘",
        key="nav_journal",
        help="Journal",
        use_container_width=True,
        type="primary" if st.session_state.active_page == "journal" else "secondary",
    ):
        st.session_state.active_page = "journal"
        st.rerun()
    st.caption("Journal")

st.divider()