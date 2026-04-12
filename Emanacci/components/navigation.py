from __future__ import annotations

import streamlit as st


NAV_ITEMS = [
    ("dashboard", "Dashboard", "Überblick, Watchlist, schneller Einstieg"),
    ("analyse", "Analyse", "Chart, Signale und Lern-Erklärungen"),
    ("paper_trading", "Paper Trading", "Üben, Positionen, Orders"),
    ("journal", "Journal", "Fehler erkennen und daraus lernen"),
    ("backtest", "Backtest", "Strategie testen und Kennzahlen prüfen"),
    ("settings", "Einstellungen", "App-Optionen, Backup, Reset"),
]


def ensure_navigation_state(default_page: str = "dashboard") -> None:
    """Sorgt dafür, dass die Seiten-Navigation im Session State existiert."""
    if "active_page" not in st.session_state:
        st.session_state.active_page = default_page


def render_sidebar_navigation() -> str:
    """Zeigt die neue Sidebar-Navigation an und gibt die gewählte Seite zurück."""
    ensure_navigation_state()

    with st.sidebar:
        st.markdown("### Emanacci")
        st.caption("Analyse, Lernen und Trading klarer strukturieren")
        st.markdown("---")

        st.markdown("#### Navigation")
        for page_key, label, help_text in NAV_ITEMS:
            is_active = st.session_state.active_page == page_key
            button_label = f"● {label}" if is_active else label
            if st.button(button_label, key=f"nav_btn_{page_key}", width="stretch", help=help_text):
                st.session_state.active_page = page_key

        st.markdown("---")
        st.caption(
            "Phase 1: Nur die Struktur wird vorbereitet. "
            "Die bestehenden Inhalte in app.py bleiben zunächst erhalten."
        )

    return st.session_state.active_page


def render_page_header(title: str, subtitle: str) -> None:
    """Ein einfacher, wiederverwendbarer Seitenkopf."""
    st.markdown(
        f"""
        <div class="em-hero">
            <div class="em-hero-title">{title}</div>
            <div class="em-hero-sub">{subtitle}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
