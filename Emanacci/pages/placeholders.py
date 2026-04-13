from __future__ import annotations

import streamlit as st

from components.navigation import render_page_header



def render_dashboard_placeholder() -> None:
    render_page_header(
        "Dashboard",
        "Hier bauen wir als Nächstes deinen klaren Startscreen mit Überblick, Watchlist und Lernhinweisen.",
    )
    st.info("Platzhalter aktiv: Dieser Bereich wird im nächsten Schritt mit echten Inhalten gefüllt.")



def render_analyse_placeholder() -> None:
    render_page_header(
        "Analyse",
        "Hier kommt dein neuer Analyse-Screen mit Hauptchart, Signalen und einfacher Erklärung hin.",
    )
    st.info("Platzhalter aktiv: Im nächsten Schritt ziehen wir die Analyse sauber aus app.py heraus.")



def render_paper_trading_placeholder():
    st.title("Paper Trading")

    trade = st.session_state.get("paper_trade_idea")

    if trade:
        st.subheader("Übernommene Trade Idee")

        st.write(f"**Symbol:** {trade['symbol']}")
        st.write(f"Entry: {trade['entry']:.2f}")
        st.write(f"Stop Loss: {trade['stop_loss']:.2f}")
        st.write(f"Take Profit: {trade['take_profit']:.2f}")
        st.write(f"RR: {trade['rr']:.2f}")

        st.success("Trade wurde aus Analyse übernommen ✅")

    else:
        st.info("Noch kein Trade übernommen.")



def render_journal_placeholder() -> None:
    render_page_header(
        "Journal",
        "Hier entsteht später dein Lernbereich mit Fehlern, Reviews und Auswertungen.",
    )
    st.info("Platzhalter aktiv: Journal wird in einer späteren Etappe aufgebaut.")



def render_backtest_placeholder() -> None:
    render_page_header(
        "Backtest",
        "Hier kommt später der Strategie-Bereich mit Regeln, Equity Curve und Kennzahlen hin.",
    )
    st.info("Platzhalter aktiv: Backtest wird später als eigene Seite ausgebaut.")



def render_settings_placeholder() -> None:
    render_page_header(
        "Einstellungen",
        "Hier bündeln wir später Reset, Backup, Theme und weitere App-Einstellungen.",
    )
    st.info("Platzhalter aktiv: Einstellungen folgen, sobald Navigation und Analyse sauber stehen.")
