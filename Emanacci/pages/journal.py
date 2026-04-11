import pandas as pd
import streamlit as st

def _calculate_progress(df: pd.DataFrame):
    if len(df) < 20:
        return None

    df = df.tail(20)

    recent = df.tail(10)
    previous = df.head(10)

    def mistake_count(data, mistake_type):
        return len(data[data["main_mistake_type"] == mistake_type])

    results = []

    for m_type in ["Timing-Fehler", "Trend-Fehler", "Risiko-Fehler"]:
        recent_count = mistake_count(recent, m_type)
        previous_count = mistake_count(previous, m_type)

        if recent_count < previous_count:
            results.append((m_type, "besser"))
        elif recent_count > previous_count:
            results.append((m_type, "schlechter"))

    # Winrate Vergleich
    def winrate(data):
        wins = len(data[data["pnl"] > 0])
        total = len(data)
        return wins / total if total > 0 else 0

    recent_wr = winrate(recent)
    prev_wr = winrate(previous)

    winrate_trend = None
    if recent_wr > prev_wr:
        winrate_trend = "besser"
    elif recent_wr < prev_wr:
        winrate_trend = "schlechter"

    return results, winrate_trend

def _build_trader_profile(df: pd.DataFrame):
    if df.empty or "main_mistake_type" not in df.columns:
        return None

    profile_df = df[
        df["main_mistake_type"].astype(str).str.strip().ne("-")
    ].copy()

    if profile_df.empty:
        return None

    counts = (
        profile_df["main_mistake_type"]
        .astype(str)
        .value_counts()
        .to_dict()
    )

    timing_count = counts.get("Timing-Fehler", 0)
    trend_count = counts.get("Trend-Fehler", 0)
    risk_count = counts.get("Risiko-Fehler", 0)

    dominant_type = max(counts, key=counts.get)

    profile_title = "Noch kein klares Profil"
    profile_text = "Es sind noch zu wenige eindeutige Muster erkennbar."

    if dominant_type == "Timing-Fehler":
        profile_title = "Du bist aktuell eher ein schneller Entscheider"
        profile_text = (
            "Du steigst eher früh ein. Das kann Chancen bringen, "
            "führt aber oft zu Einstiegen ohne saubere Bestätigung."
        )
    elif dominant_type == "Trend-Fehler":
        profile_title = "Du handelst aktuell zu oft gegen die Richtung"
        profile_text = (
            "Du versuchst häufiger Bewegungen zu erwischen, "
            "die nicht sauber zum Haupttrend passen."
        )
    elif dominant_type == "Risiko-Fehler":
        profile_title = "Du planst aktuell dein Risiko noch nicht stabil genug"
        profile_text = (
            "Dein Stop-Loss, dein Chance-Risiko-Verhältnis oder deine Stückzahl "
            "passen noch nicht oft genug sauber zusammen."
        )

    strengths = []

    if timing_count == 0 and len(profile_df) >= 5:
        strengths.append("Du wartest meist auf bessere Bestätigung.")
    if trend_count == 0 and len(profile_df) >= 5:
        strengths.append("Du respektierst den Haupttrend oft gut.")
    if risk_count == 0 and len(profile_df) >= 5:
        strengths.append("Du gehst oft sauber mit Risiko um.")

    return {
        "title": profile_title,
        "text": profile_text,
        "dominant_type": dominant_type,
        "counts": counts,
        "strengths": strengths,
    }

    st.subheader("Dein Profil")

    profile = _build_trader_profile(filtered_df)
    progress = _calculate_progress(filtered_df)
    combined = _build_combined_insight(profile, progress)

    if combined:
        st.success(combined)

    if profile is None:
        st.caption("Noch kein Profil möglich, weil noch zu wenige Fehler-Muster vorhanden sind.")
    else:
        dominant_type = str(profile["dominant_type"])

        if dominant_type == "Timing-Fehler":
            st.warning(f"**{profile['title']}**\n\n{profile['text']}")
        elif dominant_type == "Trend-Fehler":
            st.warning(f"**{profile['title']}**\n\n{profile['text']}")
        elif dominant_type == "Risiko-Fehler":
            st.warning(f"**{profile['title']}**\n\n{profile['text']}")
        else:
            st.info(f"**{profile['title']}**\n\n{profile['text']}")

        c1, c2, c3 = st.columns(3)
        c1.metric("Timing-Fehler", int(profile["counts"].get("Timing-Fehler", 0)))
        c2.metric("Trend-Fehler", int(profile["counts"].get("Trend-Fehler", 0)))
        c3.metric("Risiko-Fehler", int(profile["counts"].get("Risiko-Fehler", 0)))

        if profile["strengths"]:
            st.markdown("**Was schon gut läuft**")
            for item in profile["strengths"]:
                st.write(f"- {item}")

def _build_combined_insight(profile, progress):
    if not profile:
        return None

    base_text = profile["title"]
    extra_text = ""

    if progress:
        results, winrate_trend = progress

        for m_type, trend in results:
            if m_type == profile["dominant_type"]:
                if trend == "besser":
                    extra_text = "Du wirst in diesem Bereich besser."
                elif trend == "schlechter":
                    extra_text = "Hier verschlechterst du dich aktuell."

        if not extra_text and winrate_trend:
            if winrate_trend == "besser":
                extra_text = "Deine Trefferquote verbessert sich."
            elif winrate_trend == "schlechter":
                extra_text = "Deine Trefferquote wird schlechter."

    if extra_text:
        return f"{base_text} – {extra_text}"

    return base_text


def get_setup_score(trade: dict) -> int:
    score = 0

    pnl_pct = float(trade.get("pnl_pct", 0))
    trade_type = str(trade.get("type", ""))

    if pnl_pct > 0:
        score += 2

    if pnl_pct >= 2:
        score += 1

    if trade_type in ["TP", "TP1", "TP2"]:
        score += 2

    if trade_type == "MANUAL":
        score -= 1

    if trade_type == "SL":
        score -= 2

    if trade_type == "PARTIAL":
        score += 0

    return score


def _render_latest_analysis_idea() -> None:
    idea = st.session_state.get("paper_trade_idea", {})

    if not idea:
        return

    st.subheader("Letzte Analyse-Idee")
    st.caption("Diese Daten kommen aus der Analyse-Seite und helfen dir beim späteren Journal-Eintrag.")

    diagnosis_summary = str(idea.get("diagnosis_summary", "Keine Diagnose vorhanden."))
    signal = str(idea.get("signal", "-"))
    risk = str(idea.get("risk", "-"))
    trend = str(idea.get("trend", "-"))
    rr = float(idea.get("rr", 0.0))
    main_mistake = str(idea.get("main_mistake", ""))
    main_mistake_type = str(idea.get("main_mistake_type", ""))
    warnings = idea.get("warnings", [])
    mistakes = idea.get("mistakes", [])
    mistake_types = idea.get("mistake_types", [])
    learning_step = str(idea.get("learning_step", ""))

    st.info(diagnosis_summary)

    c1, c2, c3 = st.columns(3)
    c1.metric("Signal", signal)
    c2.metric("Risiko", risk)
    c3.metric("RR", f"{rr:.2f}")

    c4, c5 = st.columns(2)
    c4.write(f"**Trend:** {trend}")
    c5.write(f"**Ticker:** {idea.get('symbol', '-')}")

    if main_mistake:
        st.error(f"❗ Hauptfehler: {main_mistake}")
        if main_mistake_type:
            st.caption(f"Typ: {main_mistake_type}")

    if warnings:
        with st.expander("Warnsignale", expanded=False):
            for item in warnings:
                st.write(f"- {item}")

    if mistakes:
        with st.expander("Typische Fehler", expanded=False):
            for idx, item in enumerate(mistakes):
                st.write(f"- {item}")
                if idx < len(mistake_types):
                    st.caption(f"Typ: {mistake_types[idx]}")

    if learning_step:
        st.markdown("**Nächster Lernschritt**")
        st.write(learning_step)

    st.divider()

def _build_weekly_review(df: pd.DataFrame):
    if df.empty:
        return None

    weekly_df = df.tail(7).copy()

    if weekly_df.empty:
        return None

    trade_count = len(weekly_df)
    total_pnl = float(weekly_df["pnl"].sum()) if "pnl" in weekly_df.columns else 0.0
    avg_pnl_pct = float(weekly_df["pnl_pct"].mean()) if "pnl_pct" in weekly_df.columns else 0.0

    wins = len(weekly_df[weekly_df["pnl"] > 0]) if "pnl" in weekly_df.columns else 0
    winrate = (wins / trade_count * 100) if trade_count > 0 else 0.0

    best_trade = None
    worst_trade = None

    if "pnl" in weekly_df.columns and not weekly_df.empty:
        best_trade = weekly_df.loc[weekly_df["pnl"].idxmax()].to_dict()
        worst_trade = weekly_df.loc[weekly_df["pnl"].idxmin()].to_dict()

    mistake_df = weekly_df[
        weekly_df["main_mistake_type"].astype(str).str.strip().ne("-")
    ].copy() if "main_mistake_type" in weekly_df.columns else pd.DataFrame()

    most_common_mistake_type = None
    if not mistake_df.empty:
        most_common_mistake_type = (
            mistake_df["main_mistake_type"]
            .astype(str)
            .value_counts()
            .idxmax()
        )

    weekly_focus = "Weiter beobachten und saubere Muster sammeln."
    if most_common_mistake_type == "Timing-Fehler":
        weekly_focus = "Diese Woche war dein Hauptthema Timing. Warte öfter auf eine Bestätigung."
    elif most_common_mistake_type == "Trend-Fehler":
        weekly_focus = "Diese Woche war dein Hauptthema Trend. Achte stärker auf die Markt-Richtung."
    elif most_common_mistake_type == "Risiko-Fehler":
        weekly_focus = "Diese Woche war dein Hauptthema Risiko. Plane Stop-Loss und Ziel sauberer."

    return {
        "trade_count": trade_count,
        "total_pnl": total_pnl,
        "avg_pnl_pct": avg_pnl_pct,
        "winrate": winrate,
        "best_trade": best_trade,
        "worst_trade": worst_trade,
        "most_common_mistake_type": most_common_mistake_type,
        "weekly_focus": weekly_focus,
    }

def render_journal_page() -> None:
    st.title("Journal")
    st.caption("Hier siehst du abgeschlossene Trades und – wenn vorhanden – die letzte Analyse-Idee aus der Analyse-Seite.")

    if st.session_state.get("advanced_mode", False):
        st.info("Advanced-Modus – volle Auswertung sichtbar")
    else:
        st.success("Anfänger-Modus – Fokus auf Lernen und Fehler")

    _render_latest_analysis_idea()

    journal = st.session_state.get("trade_journal", [])

    if not journal:
        st.info("Noch keine abgeschlossenen Trades vorhanden.")
        return

    scored_journal = []
    for trade in journal:
        trade_copy = trade.copy()
        trade_copy["setup_score"] = get_setup_score(trade)
        scored_journal.append(trade_copy)

    df = pd.DataFrame(scored_journal)

    required_defaults = {
        "symbol": "-",
        "type": "-",
        "entry": 0.0,
        "exit": 0.0,
        "pnl": 0.0,
        "pnl_pct": 0.0,
        "setup_score": 0,
        "signal": "-",
        "risk": "-",
        "trend": "-",
        "strength": "-",
        "main_mistake": "-",
        "main_mistake_type": "-",
    }

    for col, default_value in required_defaults.items():
        if col not in df.columns:
            df[col] = default_value

    # =====================================================
    # FILTER
    # =====================================================
    st.subheader("Filter")

    f1, f2 = st.columns(2)

    with f1:
        symbol_options = ["Alle"] + sorted(
            [str(x) for x in df["symbol"].dropna().astype(str).unique().tolist()]
        )
        selected_symbol = st.selectbox(
            "Symbol",
            symbol_options,
            key="journal_symbol_filter",
        )

    with f2:
        type_options = ["Alle"] + sorted(
            [str(x) for x in df["type"].dropna().astype(str).unique().tolist()]
        )
        selected_type = st.selectbox(
            "Typ",
            type_options,
            key="journal_type_filter",
        )

    filtered_df = df.copy()
    is_advanced = st.session_state.get("advanced_mode", False)

    if selected_symbol != "Alle":
        filtered_df = filtered_df[filtered_df["symbol"].astype(str) == selected_symbol]

    if selected_type != "Alle":
        filtered_df = filtered_df[filtered_df["type"].astype(str) == selected_type]

    if filtered_df.empty:
        st.warning("Keine Trades für diesen Filter gefunden.")
        return

    # =====================================================
    # METRICS
    # =====================================================
    wins_df = filtered_df[filtered_df["pnl"] > 0]
    losses_df = filtered_df[filtered_df["pnl"] <= 0]

    trades_count = len(filtered_df)
    winrate = (len(wins_df) / trades_count * 100) if trades_count > 0 else 0.0
    avg_pnl_pct = float(filtered_df["pnl_pct"].mean()) if trades_count > 0 else 0.0
    total_pnl = float(filtered_df["pnl"].sum()) if trades_count > 0 else 0.0

    m1, m2 = st.columns(2)
    m1.metric("Trades", int(trades_count))
    m2.metric("Winrate", f"{winrate:.1f}%")

    m3, m4 = st.columns(2)
    m3.metric("Ø PnL %", f"{avg_pnl_pct:.2f}%")
    m4.metric("Gesamt PnL", f"{total_pnl:.2f}")

    st.divider()

    # =====================================================
    # VISUELLE AUSWERTUNG
    # =====================================================
    if is_advanced:
        st.subheader("Trade-Historie visuell")

        st.write("**PnL pro Trade**")
        pnl_chart_df = filtered_df.reset_index(drop=True).copy()
        pnl_chart_df.index = pnl_chart_df.index + 1
        st.bar_chart(pnl_chart_df[["pnl"]], width="stretch")

        st.write("**Gewinner vs Verlierer**")
        wl_df = pd.DataFrame(
            {"Anzahl": [len(wins_df), len(losses_df)]},
            index=["Gewinner", "Verlierer"],
        )
        st.bar_chart(wl_df, width="stretch")

        st.divider()

    # =====================================================
    # BESTE / SCHWÄCHSTE TRADES
    # =====================================================
    if is_advanced:
        st.subheader("Pro Trade Analyse")

        best_trades = filtered_df.sort_values("setup_score", ascending=False).head(3)
        worst_trades = filtered_df.sort_values("setup_score", ascending=True).head(3)

        st.write("**Beste Trades**")
        for _, row in best_trades.iterrows():
            with st.container(border=True):
                c1, c2 = st.columns(2)
                c1.write(f"**{row['symbol']}**")
                c2.write(f"**Typ:** {row['type']}")
                st.write(f"Entry: {float(row['entry']):.2f}")
                st.write(f"Exit: {float(row['exit']):.2f}")
                st.write(f"PnL: {float(row['pnl']):.2f}")
                st.write(f"PnL %: {float(row['pnl_pct']):.2f}%")
                st.write(f"Setup Score: {int(row['setup_score'])}")

        st.write("**Schwächste Trades**")
        for _, row in worst_trades.iterrows():
            with st.container(border=True):
                c1, c2 = st.columns(2)
                c1.write(f"**{row['symbol']}**")
                c2.write(f"**Typ:** {row['type']}")
                st.write(f"Entry: {float(row['entry']):.2f}")
                st.write(f"Exit: {float(row['exit']):.2f}")
                st.write(f"PnL: {float(row['pnl']):.2f}")
                st.write(f"PnL %: {float(row['pnl_pct']):.2f}%")
                st.write(f"Setup Score: {int(row['setup_score'])}")

        st.divider()

    # =====================================================
    # AUSWERTUNG / FEEDBACK
    # =====================================================
    st.subheader("Auswertung")

    types = filtered_df["type"].astype(str).tolist()
    most_common_type = max(set(types), key=types.count) if types else None

    st.write(f"Ø Ergebnis: {avg_pnl_pct:.2f}%")

    if most_common_type == "SL":
        st.warning("Du wirst häufig ausgestoppt → Stop Loss eventuell zu eng oder Einstieg zu früh.")
    elif most_common_type == "TP2":
        st.success("Viele Trades laufen bis TP2 → sehr gutes Trade Management.")
    elif most_common_type == "TP1":
        st.info("Viele Trades erreichen TP1 → Teilgewinn klappt gut, vielleicht läuft noch mehr.")
    elif most_common_type == "MANUAL":
        st.info("Viele Trades werden manuell geschlossen → vielleicht greifst du zu früh ein.")
    elif most_common_type == "PARTIAL":
        st.info("Du nutzt oft Teilverkäufe → gutes Risiko-Management, aber prüfe den Rest-Exit.")
    else:
        st.caption("Noch keine klare Tendenz im Verhalten erkennbar.")

    st.divider()

    # =====================================================
    # FEHLER-TYPEN AUSWERTUNG
    # =====================================================
    st.subheader("Fehler-Typen")

    mistake_df = filtered_df.copy()
    mistake_df = mistake_df[
        mistake_df["main_mistake_type"].astype(str).str.strip().ne("-")
    ]

    type_counts = pd.DataFrame(columns=["Fehler-Typ", "Anzahl"])

    if not mistake_df.empty:
        type_counts = (
            mistake_df["main_mistake_type"]
            .astype(str)
            .value_counts()
            .rename_axis("Fehler-Typ")
            .reset_index(name="Anzahl")
        )

        most_common_mistake_type = str(type_counts.iloc[0]["Fehler-Typ"])

        c1, c2 = st.columns(2)

        with c1:
            st.write("**Häufigste Fehler-Typen**")
            st.bar_chart(
                type_counts.set_index("Fehler-Typ")[["Anzahl"]],
                width="stretch",
            )

        with c2:
            st.write("**Wichtigster aktueller Lernpunkt**")
            st.metric("Häufigster Fehler-Typ", most_common_mistake_type)

            if most_common_mistake_type == "Timing-Fehler":
                st.warning("Du steigst oft zu früh ein. Warte öfter auf eine klare Bestätigung.")
            elif most_common_mistake_type == "Trend-Fehler":
                st.warning("Du handelst zu oft gegen die Markt-Richtung. Achte stärker auf den Haupttrend.")
            elif most_common_mistake_type == "Risiko-Fehler":
                st.warning("Dein Risiko oder dein Chance-Risiko-Verhältnis ist oft nicht sauber genug.")
            else:
                st.info("Es gibt einen wiederkehrenden Fehler-Typ. Prüfe deine letzten Trades genauer.")

        with st.expander("Details zu Fehler-Typen", expanded=False):
            st.dataframe(type_counts, width="stretch")
    else:
        st.caption("Noch keine Fehler-Typen in den Journal-Daten vorhanden.")

    st.divider()

    # =====================================================
    # LERN-ZUSAMMENFASSUNG
    # =====================================================
    st.subheader("Lern-Zusammenfassung")

    if not mistake_df.empty and not type_counts.empty:
        most_common_mistake_type = str(type_counts.iloc[0]["Fehler-Typ"])

        learning_title = "Noch kein klarer Lernfokus"
        learning_text = "Sammle erst noch mehr Trades, damit Muster klarer sichtbar werden."

        if most_common_mistake_type == "Timing-Fehler":
            learning_title = "Dein Fokus: besseres Timing"
            learning_text = (
                "Du steigst aktuell oft zu früh ein. "
                "Warte öfter auf eine klare Bestätigung, bevor du einen Trade eröffnest."
            )
        elif most_common_mistake_type == "Trend-Fehler":
            learning_title = "Dein Fokus: Trend besser respektieren"
            learning_text = (
                "Du handelst aktuell zu oft gegen die Markt-Richtung. "
                "Achte stärker darauf, ob der Haupttrend wirklich zu deinem Einstieg passt."
            )
        elif most_common_mistake_type == "Risiko-Fehler":
            learning_title = "Dein Fokus: Risiko sauberer planen"
            learning_text = (
                "Dein Risiko oder dein Chance-Risiko-Verhältnis ist oft noch nicht sauber genug. "
                "Plane Stop-Loss, Ziel und Stückzahl bewusster."
            )

        st.info(f"**{learning_title}**\n\n{learning_text}")

        if "main_mistake" in mistake_df.columns:
            common_mistakes = (
                mistake_df["main_mistake"]
                .astype(str)
                .value_counts()
                .rename_axis("Fehler")
                .reset_index(name="Anzahl")
            )

            if not common_mistakes.empty:
                top_mistake = str(common_mistakes.iloc[0]["Fehler"])
                st.caption(f"Häufigster konkreter Fehler: {top_mistake}")
    else:
        st.caption("Noch keine Lern-Zusammenfassung möglich, weil noch keine Fehler-Typen vorhanden sind.")

    st.subheader("Dein Fortschritt")

    progress = _calculate_progress(filtered_df)

    if progress is None:
        st.caption("Noch nicht genug Trades für eine Fortschrittsanalyse (mind. 20 nötig).")
    else:
        results, winrate_trend = progress

        if not results and not winrate_trend:
            st.info("Noch keine klare Veränderung erkennbar.")

        for m_type, trend in results:
            if trend == "besser":
                st.success(f"Du wirst besser bei: {m_type}")
            elif trend == "schlechter":
                st.warning(f"Hier verschlechterst du dich: {m_type}")

        if winrate_trend == "besser":
            st.success("Deine Trefferquote verbessert sich.")
        elif winrate_trend == "schlechter":
            st.warning("Deine Trefferquote wird schlechter.")

    st.divider()

    st.subheader("Wochen-Review")

    weekly_review = _build_weekly_review(filtered_df)

    if weekly_review is None:
        st.caption("Noch keine Wochen-Zusammenfassung möglich.")
    else:
        st.info(weekly_review["weekly_focus"])

        w1, w2 = st.columns(2)
        w1.metric("Trades", int(weekly_review["trade_count"]))
        w2.metric("Winrate", f'{weekly_review["winrate"]:.1f}%')

        w3, w4 = st.columns(2)
        w3.metric("Gesamt PnL", f'{weekly_review["total_pnl"]:.2f}')
        w4.metric("Ø PnL %", f'{weekly_review["avg_pnl_pct"]:.2f}%')

        if weekly_review["most_common_mistake_type"]:
            st.write(f"**Häufigster Fehler-Typ:** {weekly_review['most_common_mistake_type']}")

        best_trade = weekly_review["best_trade"]
        if best_trade:
            with st.container(border=True):
                st.write("**Bester Trade der Woche**")
                st.write(f"Symbol: {best_trade.get('symbol', '-')}")
                st.write(f"Typ: {best_trade.get('type', '-')}")
                st.write(f"PnL: {float(best_trade.get('pnl', 0.0)):.2f}")
                st.write(f"PnL %: {float(best_trade.get('pnl_pct', 0.0)):.2f}%")

        worst_trade = weekly_review["worst_trade"]
        if worst_trade:
            with st.container(border=True):
                st.write("**Schwächster Trade der Woche**")
                st.write(f"Symbol: {worst_trade.get('symbol', '-')}")
                st.write(f"Typ: {worst_trade.get('type', '-')}")
                st.write(f"PnL: {float(worst_trade.get('pnl', 0.0)):.2f}")
                st.write(f"PnL %: {float(worst_trade.get('pnl_pct', 0.0)):.2f}%")
                if str(worst_trade.get("main_mistake", "-")) not in ["-", "", "nan"]:
                    st.caption(f"Hauptfehler: {worst_trade.get('main_mistake')}")

    st.subheader("Dein nächstes Lernziel")

    st.subheader("Dein Level")

    level_data = _build_level_system(filtered_df)

    if level_data["level"] == "Anfänger":
        st.warning(f"Level: {level_data['level']}")
    elif level_data["level"] == "Lernender":
        st.info(f"Level: {level_data['level']}")
    elif level_data["level"] == "Solider Trader":
        st.success(f"Level: {level_data['level']}")
    else:
        st.success(f"Level: {level_data['level']}")

    l1, l2 = st.columns(2)
    l1.metric("Level-Punkte", int(level_data["score"]))
    l2.metric("Nächstes Ziel", level_data["next_level"])

    l3, l4 = st.columns(2)
    l3.metric("Trades", int(level_data["trade_count"]))
    l4.metric("Winrate", f"{level_data['winrate']:.1f}%")

    st.caption(level_data["hint"])

    progress_value = min(level_data["score"] / 7, 1.0)
    st.progress(progress_value)

    progress = _calculate_progress(filtered_df)
    learning_goal = _build_next_learning_goal(filtered_df, progress)

    if learning_goal:
        st.success(learning_goal)
    else:
        st.caption("Noch kein klares Lernziel ableitbar.")

    # =====================================================
    # LETZTE TRADES KOMPAKT (MOBILE)
    # =====================================================
    st.subheader("Letzte Trades kompakt")

    latest_trades = filtered_df.tail(5).iloc[::-1]

    for _, row in latest_trades.iterrows():
        with st.container(border=True):
            top1, top2 = st.columns(2)
            top1.write(f"**{row['symbol']}**")
            top2.write(f"**{row['type']}**")

            mid1, mid2 = st.columns(2)
            mid1.metric("PnL", f"{float(row['pnl']):.2f}")
            mid2.metric("PnL %", f"{float(row['pnl_pct']):.2f}%")

            if str(row.get("main_mistake", "-")) not in ["-", "", "nan"]:
                st.caption(f"Hauptfehler: {row['main_mistake']}")

    st.divider()

    # =====================================================
    # TABELLE
    # =====================================================
    if is_advanced:
        st.subheader("Alle Trades")

        preferred_order = [
            "symbol",
            "entry",
            "exit",
            "pnl",
            "pnl_pct",
            "type",
            "setup_score",
            "signal",
            "risk",
            "trend",
            "main_mistake",
            "main_mistake_type",
        ]

        display_cols = [col for col in preferred_order if col in filtered_df.columns]

        with st.expander("Tabelle anzeigen", expanded=False):
            st.dataframe(filtered_df[display_cols], width="stretch")

def _build_next_learning_goal(df: pd.DataFrame, progress):
    if df.empty:
        return None

    mistake_df = df[
        df["main_mistake_type"].astype(str).str.strip().ne("-")
    ].copy()

    if mistake_df.empty:
        return "Sammle weitere Trades, um klare Muster zu erkennen."

    most_common = (
        mistake_df["main_mistake_type"]
        .astype(str)
        .value_counts()
        .idxmax()
    )

    goal = ""

    if most_common == "Timing-Fehler":
        goal = "Konzentriere dich darauf, erst nach einer klaren Bestätigung einzusteigen."
    elif most_common == "Trend-Fehler":
        goal = "Achte stärker darauf, nur in Richtung des Haupttrends zu handeln."
    elif most_common == "Risiko-Fehler":
        goal = "Plane Stop-Loss, Ziel und Positionsgröße bewusster."
    else:
        goal = "Achte auf saubere Einstiege und gutes Risiko-Management."

    # Fortschritt einbauen
    if progress:
        results, _ = progress

        for m_type, trend in results:
            if m_type == most_common:
                if trend == "besser":
                    goal += " Du wirst hier bereits besser – bleib dran."
                elif trend == "schlechter":
                    goal += " Hier verschlechterst du dich aktuell – besonders darauf achten."

    return goal

def _build_level_system(df: pd.DataFrame):
    if df.empty:
        return {
            "level": "Anfänger",
            "score": 0,
            "next_level": "Lernender",
            "hint": "Starte mit ersten Trades und sammle Erfahrungen.",
        }

    trade_count = len(df)

    wins = len(df[df["pnl"] > 0]) if "pnl" in df.columns else 0
    winrate = (wins / trade_count * 100) if trade_count > 0 else 0.0

    mistake_df = df[
        df["main_mistake_type"].astype(str).str.strip().ne("-")
    ].copy() if "main_mistake_type" in df.columns else pd.DataFrame()

    mistake_count = len(mistake_df)

    score = 0

    # Trade-Erfahrung
    if trade_count >= 5:
        score += 1
    if trade_count >= 15:
        score += 1
    if trade_count >= 30:
        score += 1

    # Winrate
    if winrate >= 45:
        score += 1
    if winrate >= 55:
        score += 1

    # Fehlerverhalten
    if trade_count > 0:
        mistake_ratio = mistake_count / trade_count
        if mistake_ratio <= 0.8:
            score += 1
        if mistake_ratio <= 0.5:
            score += 1
    else:
        mistake_ratio = 1.0

    if score <= 2:
        level = "Anfänger"
        next_level = "Lernender"
        hint = "Konzentriere dich zuerst auf saubere Einstiege und weniger typische Fehler."
    elif score <= 4:
        level = "Lernender"
        next_level = "Solider Trader"
        hint = "Du baust gerade Grundlagen auf. Arbeite weiter an Timing und Risiko."
    elif score <= 6:
        level = "Solider Trader"
        next_level = "Fortgeschritten"
        hint = "Deine Trades werden stabiler. Jetzt geht es um Konstanz und Disziplin."
    else:
        level = "Fortgeschritten"
        next_level = "Stabilität halten"
        hint = "Du hast bereits gute Muster aufgebaut. Halte deine Qualität konstant."

    return {
        "level": level,
        "score": score,
        "next_level": next_level,
        "hint": hint,
        "trade_count": trade_count,
        "winrate": winrate,
        "mistake_ratio": mistake_ratio,
    }