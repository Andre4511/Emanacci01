import pandas as pd
import streamlit as st
import plotly.graph_objects as go
import datetime

from utils import load_data
from pages.journal import (
    _build_level_system,
    _build_next_learning_goal,
    _build_trader_profile,
    _calculate_progress,
    _build_combined_insight,
)


def create_mini_chart(data):
    close = data["Close"].astype(float)

    price_now = float(close.iloc[-1])
    price_start = float(close.iloc[0])
    is_up = price_now >= price_start

    line_color = "#00E676" if is_up else "#FF5252"
    glow_color_1 = "rgba(0,230,118,0.16)" if is_up else "rgba(255,82,82,0.16)"
    glow_color_2 = "rgba(0,230,118,0.06)" if is_up else "rgba(255,82,82,0.06)"

    ymin = float(close.min())
    ymax = float(close.max())
    padding = (ymax - ymin) * 0.25 if ymax > ymin else (ymax * 0.01 if ymax != 0 else 1.0)

    lower_band_1 = close - padding * 0.55
    lower_band_2 = close - padding

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=data.index,
            y=close,
            mode="lines",
            line=dict(color=line_color, width=2.5),
            hoverinfo="skip",
            showlegend=False,
        )
    )

    fig.add_trace(
        go.Scatter(
            x=data.index,
            y=lower_band_1,
            mode="lines",
            line=dict(width=0),
            fill="tonexty",
            fillcolor=glow_color_1,
            hoverinfo="skip",
            showlegend=False,
        )
    )

    fig.add_trace(
        go.Scatter(
            x=data.index,
            y=lower_band_2,
            mode="lines",
            line=dict(width=0),
            fill="tonexty",
            fillcolor=glow_color_2,
            hoverinfo="skip",
            showlegend=False,
        )
    )

    fig.update_layout(
        height=78,
        margin=dict(l=0, r=0, t=0, b=0),
        xaxis=dict(visible=False, fixedrange=True),
        yaxis=dict(
            visible=False,
            fixedrange=True,
            range=[float(lower_band_2.min()), ymax + padding * 0.15],
        ),
        showlegend=False,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
    )

    return fig

def _build_dashboard_status(level_data: dict, profile: dict | None, progress):
    level = str(level_data.get("level", "Anfänger"))

    if not profile:
        return {
            "color": "yellow",
            "label": "Noch wenig Daten",
            "text": "Sammle zuerst mehr Trades, damit Emanacci dein Verhalten besser einschätzen kann.",
        }

    dominant_type = str(profile.get("dominant_type", ""))
    progress_text = ""

    if progress:
        results, winrate_trend = progress

        matching_result = None
        for m_type, trend in results:
            if m_type == dominant_type:
                matching_result = trend
                break

        if matching_result == "besser":
            progress_text = "Du entwickelst dich in deinem Hauptthema gerade positiv."
        elif matching_result == "schlechter":
            progress_text = "In deinem Hauptthema gibt es aktuell Rückschritte."
        elif winrate_trend == "besser":
            progress_text = "Deine Trefferquote verbessert sich."
        elif winrate_trend == "schlechter":
            progress_text = "Deine Trefferquote wird aktuell schwächer."

    if level in ["Solider Trader", "Fortgeschritten"]:
        if progress_text and ("positiv" in progress_text or "verbessert" in progress_text):
            return {
                "color": "green",
                "label": "Stabil",
                "text": f"Dein aktueller Zustand wirkt stabil. {progress_text}",
            }

    if dominant_type == "Risiko-Fehler":
        return {
            "color": "red",
            "label": "Vorsicht",
            "text": "Dein aktuelles Hauptthema ist Risiko. Plane Stop-Loss, Ziel und Positionsgröße sauberer.",
        }

    if progress_text and "Rückschritte" in progress_text:
        return {
            "color": "red",
            "label": "Kritisch beobachten",
            "text": progress_text,
        }

    return {
        "color": "yellow",
        "label": "Gemischt",
        "text": progress_text or "Es gibt Fortschritte, aber auch noch klare Lernfelder.",
    }

def render_dashboard():
    if "watchlist" not in st.session_state:
        st.session_state.watchlist = ["TSLA", "AAPL", "NVDA"]

    if "ticker" not in st.session_state:
        st.session_state.ticker = "TSLA"

    # 👉 HIER rein
    if "seen_onboarding" not in st.session_state:
        st.session_state.seen_onboarding = False

    if "daily_task_done" not in st.session_state:
        st.session_state.daily_task_done = False

    today = datetime.date.today()

    if "last_task_date" not in st.session_state:
        st.session_state.last_task_date = today

    if st.session_state.last_task_date != today:
        st.session_state.daily_task_done = False
        st.session_state.last_task_date = today

    st.title("Dashboard")

    ticker = st.session_state.get("ticker", "TSLA")
    watchlist = st.session_state.get("watchlist", ["TSLA", "AAPL", "NVDA"])

    # =====================================================
    # TÄGLICHE AUFGABE (NEU)
    # =====================================================

    tasks = [
        "Beobachte heute einen Trend (steigend oder fallend)",
        "Achte darauf, ob der Kurs über oder unter der EMA liegt",
        "Suche einen möglichen Einstieg – aber handle noch nicht",
        "Vergleiche Risiko und Chance bei einem Trade",
        "Erkenne: Ist der Markt klar oder unsicher?",
    ]

    today_index = datetime.date.today().toordinal() % len(tasks)
    today_task = tasks[today_index]

    # =====================================================
    # ONBOARDING (NEU)
    # =====================================================

    if not st.session_state.seen_onboarding:
        with st.container(border=True):
            st.markdown("### 👋 Willkommen bei Emanacci")

            st.write("So startest du:")
            st.write("1. Öffne die Analyse")
            st.write("2. Schau dir den Chart an")
            st.write("3. Teste einen Trade")

            if st.button("Verstanden", use_container_width=True, key="onboarding_ok"):
                st.session_state.seen_onboarding = True
                st.rerun()

            # =====================================================
            # TÄGLICHE AUFGABE
            # =====================================================

            with st.container(border=True):
                st.markdown("### 📘 Heute für dich")

                st.write(today_task)

                if not st.session_state.daily_task_done:
                    if st.button("✅ Erledigt", use_container_width=True, key="task_done_btn"):
                        st.session_state.daily_task_done = True
                        st.rerun()
                else:
                    st.success("✔ Aufgabe abgeschlossen")

    # =====================================================
    # DEIN FORTSCHRITT
    # =====================================================

    journal = st.session_state.get("trade_journal", [])

    if journal:
        df = pd.DataFrame(journal)

        level_data = _build_level_system(df)
        progress = _calculate_progress(df)
        profile = _build_trader_profile(df)
        learning_goal = _build_next_learning_goal(df, progress)

        combined = _build_combined_insight(profile, progress)
        dashboard_status = _build_dashboard_status(level_data, profile, progress)

        st.markdown('<div class="em-section-card">', unsafe_allow_html=True)
        st.markdown('<div class="em-section-title">Dein Fortschritt</div>', unsafe_allow_html=True)

        level_names = [
            "Anfänger",
            "Lernender",
            "Solider Trader",
            "Fortgeschritten"
        ]

        current_level = level_data.get("level", "Anfänger")

        try:
            idx = level_names.index(current_level)
            next_level = level_names[idx + 1] if idx < len(level_names) - 1 else None
        except ValueError:
            next_level = None

        # AMPELSTATUS
        if dashboard_status["color"] == "green":
            st.success(f"🟢 Gesamtstatus: {dashboard_status['label']}")
        elif dashboard_status["color"] == "red":
            st.error(f"🔴 Gesamtstatus: {dashboard_status['label']}")
        else:
            st.warning(f"🟡 Gesamtstatus: {dashboard_status['label']}")

        st.caption(dashboard_status["text"])

        # LEVEL
        if level_data["level"] == "Anfänger":
            st.warning(f"Level: {level_data['level']}")
        elif level_data["level"] == "Lernender":
            st.info(f"Level: {level_data['level']}")
        else:
            st.success(f"Level: {level_data['level']}")

        st.progress(min(level_data["score"] / 7, 1.0))

        if next_level:
            st.caption(f"Nächstes Level: {next_level}")
        else:
            st.success("Maximales Level erreicht 🚀")

        # LERNZIEL
        if learning_goal:
            st.markdown("**Dein Fokus**")
            st.write(learning_goal)

        # PROFIL KURZ
        if profile:
            st.markdown("**Dein Verhalten**")
            st.caption(profile["title"])

        st.markdown("</div>", unsafe_allow_html=True)

        if combined:
            st.markdown("**Kurzfazit**")
            st.write(combined)

        st.divider()

    # =====================================================
    # SCHNELLÜBERBLICK
    # =====================================================
    st.markdown('<div class="em-section-card">', unsafe_allow_html=True)
    st.markdown("### Schnellüberblick")
    st.caption("Dein aktuelles Symbol auf einen Blick")

    data = load_data(ticker, "1mo", "1d")

    if not data.empty:
        current_price = float(data["Close"].iloc[-1])
        prev_price = float(data["Close"].iloc[-2]) if len(data) > 1 else current_price
        change_pct = ((current_price - prev_price) / prev_price * 100) if prev_price != 0 else 0.0

        if change_pct > 1:
            market_status = "Positiv"
        elif change_pct < -1:
            market_status = "Schwach"
        else:
            market_status = "Neutral"

        c1, c2, c3 = st.columns(3)
        c1.metric("Symbol", ticker)
        c2.metric("Kurs", f"{current_price:.2f} USD")
        c3.metric("Tagesänderung", f"{change_pct:.2f}%")

        st.info(f"Aktueller Marktstatus für **{ticker}**: **{market_status}**")

        if st.button("🔍 Analyse öffnen", use_container_width=True):
            st.session_state.active_page = "analyse"
            st.rerun()
    else:
        st.warning("Für das aktuelle Symbol konnten keine Daten geladen werden.")

    st.markdown("</div>", unsafe_allow_html=True)

    st.divider()
    st.markdown("### ⭐ Watchlist")

    # =====================================================
    # WATCHLIST
    # =====================================================
    st.markdown('<div class="em-section-card">', unsafe_allow_html=True)
    st.markdown('<div class="em-section-title">Watchlist</div>', unsafe_allow_html=True)
    st.markdown('<div class="em-section-sub">Deine beobachteten Werte mit Schnellzugriff</div>', unsafe_allow_html=True)

    new_symbol = st.text_input(
        "Symbol zur Watchlist hinzufügen",
        key="dashboard_new_watchlist_symbol",
    ).upper().strip()

    if st.button("Hinzufügen", width="stretch", key="dashboard_add_watchlist_symbol"):
        if new_symbol and new_symbol not in st.session_state.watchlist:
            st.session_state.watchlist.append(new_symbol)
            st.success(f"{new_symbol} hinzugefügt")
            st.rerun()

    if watchlist:
        num_cols = 2
        cols = st.columns(num_cols)

        for i, symbol in enumerate(watchlist):
            with cols[i % num_cols]:
                symbol_data = load_data(symbol, "1mo", "1d")

                with st.container(border=True):
                    top_left, top_right = st.columns([4, 1])

                    with top_left:
                        if st.button(
                            f"{symbol}",
                            key=f"open_{symbol}",
                            use_container_width=True,
                            type="secondary",
                        ):
                            st.session_state.ticker = symbol
                            st.session_state.active_page = "analyse"
                            st.rerun()

                        if not symbol_data.empty:
                            price = float(symbol_data["Close"].iloc[-1])
                            prev = float(symbol_data["Close"].iloc[-2]) if len(symbol_data) > 1 else price
                            change = ((price - prev) / prev * 100) if prev != 0 else 0.0
                            st.caption(f"{price:.2f} USD | {change:.2f}%")
                        else:
                            st.caption("Keine Daten verfügbar")

                    with top_right:
                        if st.button("✕", key=f"delete_{symbol}"):
                            st.session_state.watchlist.remove(symbol)
                            st.rerun()

                    if not symbol_data.empty:
                        mini_fig = create_mini_chart(symbol_data)
                        st.plotly_chart(mini_fig, width="stretch", config={"displayModeBar": False})
    else:
        st.info("Deine Watchlist ist aktuell leer.")

    st.markdown("</div>", unsafe_allow_html=True)