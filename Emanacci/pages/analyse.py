import streamlit as st

from indicators import calculate_indicators
from utils import load_data
from components.charts import create_main_chart


def _init_session_state() -> None:
    defaults = {
        "ticker": "TSLA",
        "period": "6mo",
        "interval": "1d",
        "show_volume": True,
        "show_rsi": True,
        "show_ema": True,
        "risk_amount_eur": 100.0,
        "show_raw_data": False,
        "zoom": "3M",
        "advanced_mode": False,
        "last_zoom": "3M",
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

    if "confirm_trade" not in st.session_state:
        st.session_state.confirm_trade = False

    if "last_symbol" not in st.session_state:
        st.session_state.last_symbol = "TSLA"


def _get_period_interval() -> tuple[str, str]:
    zoom_map = {
        "1D": ("1d", "5m"),
        "1W": ("7d", "1h"),
        "1M": ("1mo", "1d"),
        "3M": ("3mo", "1d"),
        "6M": ("6mo", "1d"),
        "1Y": ("1y", "1d"),
    }
    return zoom_map.get(st.session_state.zoom, ("3mo", "1d"))


def render_analyse_page() -> None:
    _init_session_state()

    st.title("Analyse")

    if st.session_state.advanced_mode:
        st.info("Advanced-Modus aktiv – erweiterte Analyse sichtbar")
    else:
        st.success("Anfänger-Modus – einfache Erklärung aktiv")

    st.caption("Wähle zuerst eine Aktie und einen Zeitraum.")

    # =====================
    # MODUS UMSCHALTER
    # =====================

    if "mode" not in st.session_state:
        st.session_state.mode = "Anfänger"

    mode_col1, mode_col2 = st.columns(2)

    with mode_col1:
        if st.button("🟢 Anfänger", use_container_width=True):
            st.session_state.mode = "Anfänger"
            st.rerun()

    with mode_col2:
        if st.button("⚙️ Advanced", use_container_width=True):
            st.session_state.mode = "Advanced"
            st.rerun()

    st.caption(f"Aktueller Modus: {st.session_state.mode}")

    # =====================================================
    # TOP BAR / STEUERUNG
    # =====================================================
    ticker_input = st.text_input(
        "Symbol",
        value=st.session_state.last_symbol,
        key="analyse_ticker_input",
    ).upper().strip()

    if ticker_input:
        st.session_state.ticker = ticker_input
        st.session_state.last_symbol = ticker_input

    active_zoom = st.session_state.zoom
    z1, z2, z3, z4, z5, z6 = st.columns(6)

    def zoom_button(label: str, key: str) -> bool:
        is_active = active_zoom == label
        return st.button(
            label,
            key=key,
            use_container_width=True,
            type="primary" if is_active else "secondary",
        )

    with z1:
        if zoom_button("1D", "zoom_1d"):
            st.session_state.zoom = "1D"
            st.session_state.last_zoom = "1D"
            st.rerun()

    with z2:
        if zoom_button("1W", "zoom_1w"):
            st.session_state.zoom = "1W"
            st.session_state.last_zoom = "1W"
            st.rerun()

    with z3:
        if zoom_button("1M", "zoom_1m"):
            st.session_state.zoom = "1M"
            st.session_state.last_zoom = "1M"
            st.rerun()

    with z4:
        if zoom_button("3M", "zoom_3m"):
            st.session_state.zoom = "3M"
            st.session_state.last_zoom = "3M"
            st.rerun()

    with z5:
        if zoom_button("6M", "zoom_6m"):
            st.session_state.zoom = "6M"
            st.session_state.last_zoom = "6M"
            st.rerun()

    with z6:
        if zoom_button("1Y", "zoom_1y"):
            st.session_state.zoom = "1Y"
            st.session_state.last_zoom = "1Y"
            st.rerun()

    st.caption(f"Aktueller Zoom: {st.session_state.zoom}")

    if st.session_state.zoom == "1D":
        st.caption("Sehr kurzfristige Ansicht")

    control_left, control_right = st.columns(2)

    with control_left:
        period_options = ["5d", "1mo", "3mo", "6mo", "1y"]
        current_period = (
            st.session_state.period
            if st.session_state.period in period_options
            else "6mo"
        )
        st.session_state.period = st.selectbox(
            "Zeitraum",
            period_options,
            index=period_options.index(current_period),
            key="analyse_period_select",
        )

    with control_right:
        interval_options = ["15m", "1h", "1d"]
        current_interval = (
            st.session_state.interval
            if st.session_state.interval in interval_options
            else "1d"
        )
        st.session_state.interval = st.selectbox(
            "Intervall",
            interval_options,
            index=interval_options.index(current_interval),
            key="analyse_interval_select",
        )

    action_left, action_right = st.columns(2)

    with action_left:
        if st.button("Reload", use_container_width=True, key="analyse_reload"):
            st.rerun()

    with action_right:
        st.toggle(
            "Advanced",
            value=st.session_state.advanced_mode,
            key="advanced_mode",
        )

    if st.button("⭐ Zur Watchlist hinzufügen", use_container_width=True, key="add_to_watchlist"):
        if "watchlist" not in st.session_state:
            st.session_state.watchlist = []

        if st.session_state.ticker not in st.session_state.watchlist:
            st.session_state.watchlist.append(st.session_state.ticker)
            st.success("Zur Watchlist hinzugefügt")
        else:
            st.info("Bereits in der Watchlist")

    st.divider()

    # =====================================================
    # DATEN LADEN
    # =====================================================
    period, interval = _get_period_interval()
    data = load_data(st.session_state.ticker, period, interval)

    if data.empty:
        st.warning("Keine Daten gefunden.")
        st.stop()

    data = data.tail(300)
    data = calculate_indicators(data)

    latest_price = float(data["Close"].iloc[-1])
    latest_rsi = float(data["RSI"].iloc[-1]) if "RSI" in data.columns else 50.0
    ema20 = float(data["EMA20"].iloc[-1]) if "EMA20" in data.columns else latest_price
    ema50 = float(data["EMA50"].iloc[-1]) if "EMA50" in data.columns else latest_price

    # =====================================================
    # BASIS ANALYSE
    # =====================================================
    trend = "Bullisch" if ema20 > ema50 else "Bärisch"

    if latest_rsi > 60:
        strength = "Stark"
    elif latest_rsi < 40:
        strength = "Schwach"
    else:
        strength = "Neutral"

    hint = "Markt eher neutral"
    if trend == "Bullisch" and strength == "Stark":
        hint = "Trend läuft sauber nach oben"
    elif trend == "Bärisch" and strength == "Stark":
        hint = "Abwärtstrend dominant"

    signal = "Unklar"
    risk = "Mittel"
    action = "Beobachten"
    color = "yellow"

    if trend == "Bullisch" and strength == "Stark":
        signal = "Positiv"
        risk = "Mittel"
        action = "Beobachten oder kleiner Einstieg möglich"
        color = "green"
    elif trend == "Bärisch" and strength == "Stark":
        signal = "Negativ"
        risk = "Hoch"
        action = "Lieber nicht einsteigen"
        color = "red"

    if signal == "Positiv" and trend == "Bullisch":
        summary_text = "Trend stabil, Einstieg möglich – aber Bestätigung beachten."
    elif signal == "Negativ":
        summary_text = "Aktuell kein guter Einstieg – Risiko hoch."
    else:
        summary_text = "Noch kein klares Signal – besser beobachten."

    # =====================================================
    # TRADE STANDARDWERTE
    # =====================================================
    entry = float(st.session_state.get("analyse_entry", latest_price))
    sl_percent = float(st.session_state.get("analyse_sl_percent", 2.0))
    tp1_percent = float(st.session_state.get("analyse_tp1_percent", 4.0))
    tp2_percent = float(st.session_state.get("analyse_tp2_percent", 8.0))
    risk_amount = float(
        st.session_state.get("analyse_risk_amount", st.session_state.risk_amount_eur)
    )

    sl_price = entry * (1 - sl_percent / 100)
    tp1_price = entry * (1 + tp1_percent / 100)
    tp2_price = entry * (1 + tp2_percent / 100)

    risk_per_share = entry - sl_price
    reward_per_share = tp1_price - entry
    rr = reward_per_share / risk_per_share if risk_per_share > 0 else 0.0
    position_size = risk_amount / risk_per_share if risk_per_share > 0 else 0.0

    # =====================================================
    # SCORE + WAS FEHLT
    # =====================================================
    score = 0
    missing_factors: list[str] = []

    if latest_price > ema20 > ema50:
        score += 40
    else:
        missing_factors.append("Trend noch nicht bestätigt")

    if latest_rsi > 60:
        score += 30
    elif latest_rsi >= 40:
        score += 15
    else:
        missing_factors.append("Momentum eher schwach")

    if signal == "Positiv":
        score += 30
    elif signal == "Unklar":
        score += 15
    else:
        missing_factors.append("Kein klares Signal")

    risk_pct = abs(entry - sl_price) / entry if entry > 0 else 0.0
    if risk_pct > 0.03:
        missing_factors.append("Risiko aktuell zu hoch")

    if entry > latest_price * 1.02:
        missing_factors.append("Einstieg noch zu früh")

    # =====================
    # AMPEL SYSTEM
    # =====================

    if score >= 70:
        ampel = "grün"
        ampel_text = "Gutes Setup – aber Risiko bleibt"
    elif score >= 40:
        ampel = "gelb"
        ampel_text = "Noch kein klares Setup – lieber warten"
    else:
        ampel = "rot"
        ampel_text = "Aktuell eher riskant – kein guter Einstieg"

    # =====================================================
    # HERO BLOCK
    # =====================================================
    st.markdown('<div class="em-section-card">', unsafe_allow_html=True)

    st.markdown(f"### {summary_text}")

    if color == "green":
        st.success(f"🟢 {action}")
    elif color == "red":
        st.error(f"🔴 {action}")
    else:
        st.warning(f"🟡 {action}")

    st.markdown(f"**Score: {score} / 100**")

    if ampel == "grün":
        st.success(f"🟢 {ampel_text}")
    elif ampel == "gelb":
        st.warning(f"🟡 {ampel_text}")
    else:
        st.error(f"🔴 {ampel_text}")

    if missing_factors:
        if ampel == "grün":
            reason_title = "Was du trotzdem beachten solltest"
        elif ampel == "gelb":
            reason_title = "Warum gerade vorsichtig?"
        else:
            reason_title = "Warum aktuell riskant?"

        st.markdown(f"**{reason_title}**")

        for factor in missing_factors[:3]:
            st.caption(f"• {factor}")

    if score >= 75:
        st.success("Gutes Setup")
    elif score >= 50:
        st.warning("Mit Vorsicht")
    else:
        st.error("Eher kein guter Einstieg")

    c1, c2, c3 = st.columns(3)
    c1.metric("Signal", signal)
    c2.metric("Risiko", risk)
    c3.metric("Trend", trend)

    st.caption(hint)

    st.markdown("</div>", unsafe_allow_html=True)
    st.divider()

    # =====================
    # KONTEXT ERKLÄRUNG
    # =====================

    context_explanation = []

    if "Trend noch nicht bestätigt" in missing_factors:
        context_explanation.append("Der Markt zeigt noch keine klare Richtung.")

    if "Momentum eher schwach" in missing_factors:
        context_explanation.append("Die Bewegung hat aktuell wenig Stärke.")

    if "Kein klares Signal" in missing_factors:
        context_explanation.append("Die Indikatoren sind sich nicht einig.")

    if "Trend negativ" in missing_factors:
        context_explanation.append("Der Markt bewegt sich eher nach unten.")

    if context_explanation:
        st.markdown("**Was bedeutet das konkret?**")

        for text in context_explanation:
            st.write(f"→ {text}")

    # =====================
    # NÄCHSTER SCHRITT (EMPFEHLUNG)
    # =====================

    next_steps = []

    # Signal basiert
    if signal == "Unklar":
        next_steps.append("Warte auf eine klare Bestätigung")

    if signal == "Negativ":
        next_steps.append("Aktuell kein Einstieg sinnvoll")

    if signal == "Positiv" and rr < 1.5:
        next_steps.append("Nur mit Vorsicht – Chance/Risiko nicht optimal")

    # Trend basiert
    if trend == "Bärisch":
        next_steps.append("Eher keine Long-Position gegen den Trend")

    # Risiko basiert
    risk_pct = abs(entry - sl_price) / entry if entry else 0

    if risk_pct > 0.03:
        next_steps.append("Positionsgröße reduzieren oder Stop-Loss näher setzen")

    # Fallback
    if not next_steps:
        next_steps.append("Setup beobachten und auf Bestätigung warten")

    # Anzeige
    st.markdown("### 👉 Nächster Schritt")

    for step in next_steps[:3]:
        st.write(f"• {step}")

    # =====================================================
    # WAS FEHLT FÜR EIN BESSERES SETUP
    # =====================================================
    if missing_factors:
        st.markdown("### 🔧 Was fehlt für ein besseres Setup?")
        for factor in missing_factors:
            st.warning(factor)
        st.divider()

    # =====================================================
    # TYPISCHE FEHLER AKTUELL
    # =====================================================

    detected_mistakes = []

    if signal == "Unklar":
        detected_mistakes.append("Zu früher Einstieg möglich")

    if trend == "Bärisch" and signal != "Negativ":
        detected_mistakes.append("Du handelst gegen den Trend")

    if rr < 1.5:
        detected_mistakes.append("Chance-Risiko-Verhältnis eher schwach")

    risk_pct = abs(entry - sl_price) / entry if entry else 0
    if risk_pct > 0.03:
        detected_mistakes.append("Risiko aktuell relativ hoch")

    # =====================================================
    # FEHLER → TYP ZUORDNUNG
    # =====================================================

    detected_mistake_types = []

    mistake_type_map = {
        "Du würdest hier wahrscheinlich zu früh einsteigen": "Timing-Fehler",
        "Du handelst aktuell gegen den Trend": "Trend-Fehler",
        "Chance-Risiko-Verhältnis ist eher schwach": "Risiko-Fehler",
        "Dein Risiko ist aktuell relativ hoch": "Risiko-Fehler",
    }

    for mistake in detected_mistakes:
        if mistake in mistake_type_map:
            detected_mistake_types.append(mistake_type_map[mistake])

    # Zu früher Einstieg
    if signal == "Unklar":
        detected_mistakes.append("Du würdest hier wahrscheinlich zu früh einsteigen")

    # Gegen Trend
    if trend == "Bärisch" and signal != "Negativ":
        detected_mistakes.append("Du handelst aktuell gegen den Trend")

    # Schlechtes CRV
    if rr < 1.5:
        detected_mistakes.append("Chance-Risiko-Verhältnis ist eher schwach")

    # Risiko zu hoch
    risk_pct = abs(entry - sl_price) / entry if entry else 0
    if risk_pct > 0.03:
        detected_mistakes.append("Dein Risiko ist aktuell relativ hoch")

    if detected_mistakes:
        for mistake in detected_mistakes:
            st.error(f"❗ {mistake}")

        st.divider()

    # =====================================================
    # CHART
    # =====================================================
    st.subheader("Chart")

    if st.session_state.mode == "Anfänger":
        fig = create_main_chart(
            data,
            show_ema=True,
            show_volume=False,
            show_rsi=False,
            entry=entry,
            stop_loss=sl_price,
            tp1=tp1_price,
            tp2=tp2_price,
            qty=position_size,
            risk_amount=risk_amount,
            score=score,
            detected_mistakes=detected_mistakes,
            ampel=ampel,
        )
    else:
        fig = create_main_chart(
            data,
            show_ema=st.session_state.get("show_ema", True),
            show_volume=st.session_state.get("show_volume", True),
            show_rsi=st.session_state.get("show_rsi", True),
            entry=entry,
            stop_loss=sl_price,
            tp1=tp1_price,
            tp2=tp2_price,
            qty=position_size,
            risk_amount=risk_amount,
            score=score,
            detected_mistakes=detected_mistakes,
            ampel=ampel,
        )

    st.plotly_chart(fig, use_container_width=True)

    if st.session_state.mode == "Advanced":
        st.markdown("### ⚙️ Erweiterte Optionen")

        opt1, opt2, opt3 = st.columns(3)

        with opt1:
            st.session_state.show_ema = st.toggle("EMA", value=True)

        with opt2:
            st.session_state.show_volume = st.toggle("Volumen", value=True)

        with opt3:
            st.session_state.show_rsi = st.toggle("RSI", value=False)

    with st.expander("📘 Was bedeuten die EMA-Linien?"):
        st.write("Die EMA zeigt dir den durchschnittlichen Preis über einen Zeitraum.")
        st.write("Kurze EMA (z. B. 20) reagiert schnell auf Änderungen.")
        st.write("Lange EMA (z. B. 50 oder 200) zeigt den langfristigen Trend.")

        st.info("👉 Wenn die kurze EMA über der langen liegt, ist der Trend oft positiv.")

    with st.expander("📘 Was bedeutet der Trend hier?"):
        st.write("Ein Trend zeigt dir die aktuelle Richtung des Marktes.")

        st.write("• Steigend = Käufer dominieren")
        st.write("• Fallend = Verkäufer dominieren")
        st.write("• Seitwärts = Unsicherheit")

        st.info("👉 Anfänger sollten möglichst mit dem Trend handeln.")

    with st.expander("📘 Was bedeutet das Signal?"):
        st.write("Das Signal fasst mehrere Faktoren zusammen.")

        st.write("• Positiv = eher Einstieg möglich")
        st.write("• Unklar = lieber abwarten")
        st.write("• Negativ = eher kein Einstieg")

        st.warning("👉 Ein Signal ist keine Garantie, sondern nur eine Einschätzung.")

    # =====================
    # RISIKOPROFIL AUS ANALYSE
    # =====================

    if score >= 70 and signal == "Positiv" and risk != "Hoch":
        suggested_risk_mode = "Normal (2%)"
    elif score >= 40:
        suggested_risk_mode = "Konservativ (1%)"
    else:
        suggested_risk_mode = "Konservativ (1%)"

    # =====================================================
    # EINSTIEG CHECK
    # =====================================================
    st.markdown("### Einstieg Check")

    check_items: list[tuple[str, str]] = []

    if trend == "Bullisch":
        check_items.append(("Trend passt", "good"))
    else:
        check_items.append(("Trend gegen dich", "bad"))

    if signal == "Positiv":
        check_items.append(("Signal vorhanden", "good"))
    elif signal == "Unklar":
        check_items.append(("Signal noch nicht bestätigt", "neutral"))
    else:
        check_items.append(("Signal negativ", "bad"))

    if risk == "Mittel":
        check_items.append(("Risiko beachten", "neutral"))
    elif risk == "Hoch":
        check_items.append(("Risiko hoch", "bad"))
    else:
        check_items.append(("Risiko gut kontrollierbar", "good"))

    for text, status in check_items:
        if status == "good":
            st.success(f"✔ {text}")
        elif status == "bad":
            st.error(f"❌ {text}")
        else:
            st.warning(f"⚠ {text}")

    # =====================================================
    # CHART ERKLÄRUNG
    # =====================================================
    with st.expander("Was im Chart passiert", expanded=False):
        if latest_price > ema20 > ema50:
            st.write("- Trend wirkt stabil nach oben (über EMA).")
        elif latest_price < ema20 < ema50:
            st.write("- Abwärtstrend intakt (unter EMA).")
        else:
            st.write("- Trend nicht klar – EMA Linien gemischt.")

        if latest_rsi > 70:
            st.write("- RSI hoch – Markt könnte überkauft sein.")
        elif latest_rsi < 30:
            st.write("- RSI niedrig – mögliche Gegenbewegung.")
        else:
            st.write("- RSI im normalen Bereich.")

    st.divider()

    # =====================================================
    # AUSWERTUNG / DIAGNOSE
    # =====================================================
    positives: list[str] = []
    warnings: list[str] = []
    mistakes: list[str] = []
    learning_step = "Achte weiter auf Trend, Risiko und klare Bestätigung."

    if trend == "Bullisch":
        positives.append("Der Trend zeigt nach oben.")
    else:
        warnings.append("Der Trend zeigt aktuell nach unten.")

    if strength == "Stark":
        positives.append("Die aktuelle Bewegung ist relativ stark.")
    elif strength == "Schwach":
        warnings.append("Die Bewegung wirkt eher schwach.")

    if signal == "Positiv":
        positives.append("Das Signal ist eher positiv.")
    elif signal == "Unklar":
        warnings.append("Das Signal ist noch nicht klar genug.")
    else:
        warnings.append("Das Signal wirkt aktuell negativ.")

    if rr < 1.5:
        warnings.append("Das Chance-Risiko-Verhältnis ist eher schwach.")
        learning_step = "Lerne, wie du Einstieg, Stop-Loss und Ziele besser zueinander planst."
    elif rr >= 2.0:
        positives.append("Das Chance-Risiko-Verhältnis wirkt solide.")

    if risk == "Hoch":
        warnings.append("Das Risiko ist aktuell hoch.")
        learning_step = "Prüfe, wie du Risiko reduzieren oder auf bessere Bestätigung warten kannst."

    if signal == "Unklar":
        mistakes.append("Zu früher Einstieg (Signal nicht bestätigt)")
    if rr < 1.5:
        mistakes.append("Schlechtes Chance-Risiko-Verhältnis")
    if trend == "Bärisch":
        mistakes.append("Gegen den Trend handeln")
    if risk == "Hoch":
        mistakes.append("Zu hohes Risiko")

    diagnosis_summary = action
    if warnings:
        diagnosis_summary = f"{action} – es gibt aktuell wichtige Warnsignale."
    elif positives:
        diagnosis_summary = f"{action} – es gibt einige positive Zeichen."

    mistake_explanations = {
        "Zu früher Einstieg (Signal nicht bestätigt)": "Du steigst ein, bevor der Markt klar zeigt, wohin er will.",
        "Schlechtes Chance-Risiko-Verhältnis": "Dein möglicher Gewinn ist zu klein im Vergleich zum Risiko.",
        "Gegen den Trend handeln": "Du handelst gegen die aktuelle Marktbewegung.",
        "Zu hohes Risiko": "Du riskierst zu viel Kapital in diesem Trade.",
    }

    mistake_types = {
        "Zu früher Einstieg (Signal nicht bestätigt)": "Timing-Fehler",
        "Schlechtes Chance-Risiko-Verhältnis": "Risiko-Fehler",
        "Gegen den Trend handeln": "Trend-Fehler",
        "Zu hohes Risiko": "Risiko-Fehler",
    }

    st.markdown('<div class="em-section-card">', unsafe_allow_html=True)
    st.markdown('<div class="em-section-title">Auswertung</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="em-section-sub">Einfache Einschätzung zu Chancen, Warnsignalen und dem nächsten Lernschritt</div>',
        unsafe_allow_html=True,
    )

    if warnings:
        st.error(f"🔴 {diagnosis_summary}")
    elif positives:
        st.success(f"🟢 {diagnosis_summary}")
    else:
        st.warning(f"🟡 {diagnosis_summary}")

    col1, col2 = st.columns(2)

    with col1:
        if positives:
            st.markdown("### 🟢 Positiv")
            for item in positives:
                st.write(f"- {item}")

    with col2:
        if warnings:
            st.markdown("### 🔴 Warnsignale")
            for item in warnings:
                st.write(f"- {item}")

    if mistakes:
        st.markdown("### ⚠️ Typische Fehler")
        main_mistake = mistakes[0]
        main_type = mistake_types.get(main_mistake, "Fehler")

        st.error(f"❗ Wichtig: {main_mistake}")
        st.caption(f"Typ: {main_type}")

        if main_mistake in mistake_explanations:
            st.caption(mistake_explanations[main_mistake])

    st.markdown("### 🟡 Nächster Schritt")
    st.write(learning_step)
    st.caption(f"Aktuelles Risiko: {risk}")

    st.markdown("</div>", unsafe_allow_html=True)
    st.divider()

    # =====================================================
    # ANFÄNGER ERKLÄRUNG
    # =====================================================
    st.markdown('<div class="em-section-card">', unsafe_allow_html=True)
    st.markdown('<div class="em-section-title">Was der Markt gerade macht</div>', unsafe_allow_html=True)

    explanation = ""

    if trend == "Bullisch":
        explanation += "Der Trend zeigt nach oben. "
    else:
        explanation += "Der Trend zeigt nach unten. "

    if strength == "Stark":
        explanation += "Die Bewegung ist relativ stark. "
    elif strength == "Schwach":
        explanation += "Die Bewegung ist eher schwach. "
    else:
        explanation += "Die Stärke ist aktuell neutral. "

    if signal == "Positiv":
        explanation += "Das Signal ist eher positiv, aber kein sicherer Einstieg."
    elif signal == "Negativ":
        explanation += "Das Signal ist negativ, hier ist Vorsicht wichtig."
    else:
        explanation += "Das Signal ist nicht eindeutig."

    st.write(explanation)
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="em-section-card">', unsafe_allow_html=True)
    st.markdown('<div class="em-section-title">Was jetzt sinnvoll ist</div>', unsafe_allow_html=True)

    st.write(f"👉 {action}")

    if signal == "Unklar":
        st.write("Warte auf eine klarere Bewegung oder Bestätigung.")
    elif signal == "Positiv":
        st.write("Du kannst den Markt beobachten oder vorsichtig einsteigen.")
    else:
        st.write("Lieber abwarten oder Risiko reduzieren.")

    st.markdown("</div>", unsafe_allow_html=True)

    # =====================================================
    # LERNHINWEISE
    # =====================================================
    if not st.session_state.advanced_mode:
        with st.expander("📘 Kurz erklärt: Wichtige Begriffe"):
            st.markdown("**EMA (Exponentieller Durchschnitt)**")
            st.write(
                "Die EMA zeigt dir die durchschnittliche Kursrichtung. "
                "Wenn der Kurs über der EMA liegt, ist das oft ein Zeichen für einen Aufwärtstrend."
            )

            st.markdown("**RSI (Relative Strength Index)**")
            st.write(
                "Der RSI zeigt dir, ob eine Aktie überkauft oder überverkauft ist. "
                "Über 70 kann bedeuten: vielleicht zu stark gestiegen. "
                "Unter 30: vielleicht überverkauft."
            )

            st.markdown("**Trend einfach erklärt**")
            st.write(
                "Ein Trend zeigt die Richtung des Marktes. "
                "Steigende Hochs = Aufwärtstrend. "
                "Fallende Tiefs = Abwärtstrend."
            )

    st.divider()

    # =====================================================
    # TRADE SETUP
    # =====================================================
    expanded_state = True if st.session_state.advanced_mode else False

    with st.expander("Trade Setup planen", expanded=expanded_state):
        st.markdown('<div class="em-section-card">', unsafe_allow_html=True)
        st.markdown('<div class="em-section-title">Trade Setup</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="em-section-sub">Plane Einstieg, Risiko und mögliche Ziele</div>',
            unsafe_allow_html=True,
        )

        s1, s2 = st.columns(2)

        with s1:
            entry = st.number_input(
                "Geplanter Einstieg",
                value=float(entry),
                key="analyse_entry",
            )

        with s2:
            risk_amount = st.number_input(
                "Max. Risiko (€)",
                min_value=1.0,
                value=float(risk_amount),
                step=10.0,
                key="analyse_risk_amount",
            )

        st.session_state.risk_amount_eur = float(risk_amount)

        s3, s4 = st.columns(2)

        with s3:
            sl_percent = st.number_input(
                "Stop Loss %",
                value=float(sl_percent),
                min_value=0.1,
                step=0.1,
                key="analyse_sl_percent",
            )

        with s4:
            tp1_percent = st.number_input(
                "Take Profit 1 %",
                value=float(tp1_percent),
                min_value=0.1,
                step=0.1,
                key="analyse_tp1_percent",
            )

        tp2_percent = st.number_input(
            "Take Profit 2 %",
            value=float(tp2_percent),
            min_value=0.1,
            step=0.1,
            key="analyse_tp2_percent",
        )

        sl_price = entry * (1 - sl_percent / 100)
        tp1_price = entry * (1 + tp1_percent / 100)
        tp2_price = entry * (1 + tp2_percent / 100)

        risk_per_share = entry - sl_price
        reward_per_share = tp1_price - entry
        rr = reward_per_share / risk_per_share if risk_per_share > 0 else 0.0
        position_size = risk_amount / risk_per_share if risk_per_share > 0 else 0.0

        r1, r2, r3 = st.columns(3)
        r1.metric("Stop-Loss", f"{sl_price:.2f}")
        r2.metric("TP1", f"{tp1_price:.2f}")
        r3.metric("TP2", f"{tp2_price:.2f}")

        r4, r5 = st.columns(2)
        r4.metric("Chance/Risiko", f"{rr:.2f}")
        r5.metric("Stückzahl", f"{position_size:.2f}")

        st.markdown("</div>", unsafe_allow_html=True)

    st.divider()

    # =====================================================
    # TRADE BEWERTUNG
    # =====================================================
    if signal == "Positiv" and risk != "Hoch":
        st.success("Setup wirkt solide – Trade möglich.")
    elif signal == "Unklar":
        st.warning("Signal noch nicht bestätigt – besser abwarten.")
    else:
        st.error("Risiko aktuell hoch – Einstieg eher ungünstig.")

    # =====================================================
    # JOURNAL DATEN
    # =====================================================
    journal_mistake_types = [mistake_types.get(m, "Fehler") for m in mistakes]
    main_mistake = mistakes[0] if mistakes else None
    main_mistake_type = mistake_types.get(main_mistake, "Fehler") if main_mistake else None

    journal_diagnosis = {
        "summary": diagnosis_summary,
        "positives": positives,
        "warnings": warnings,
        "mistakes": mistakes,
        "mistake_types": journal_mistake_types,
        "main_mistake": main_mistake,
        "main_mistake_type": main_mistake_type,
        "learning_step": learning_step,
        "signal": signal,
        "risk": risk,
        "trend": trend,
        "strength": strength,
        "hint": hint,
    }

    if st.session_state.advanced_mode:
        with st.expander("Journal-Vorschau", expanded=False):
            st.json(journal_diagnosis)

    # =====================================================
    # ÜBERGABE AN PAPER TRADING
    # =====================================================
    if st.button("🚀 Trade in Paper Trading übernehmen", use_container_width=True, key="analyse_to_paper"):
        st.session_state.confirm_trade = True

    if st.session_state.confirm_trade:
        st.warning("Möchtest du diesen Trade wirklich übernehmen?")

        c1, c2 = st.columns(2)

        with c1:
            if st.button("✅ Ja, übernehmen", use_container_width=True, key="confirm_trade_yes"):
                st.session_state.paper_trade_idea = {
                    "symbol": st.session_state.ticker,
                    "entry": float(entry),
                    "stop_loss": float(sl_price),
                    "take_profit_1": float(tp1_price),
                    "take_profit_2": float(tp2_price),
                    "rr": float(rr),
                    "suggested_qty": float(position_size),
                    "risk_amount_eur": float(risk_amount),
                    "score": score,
                    "signal": signal,
                    "risk": risk,
                    "trend": trend,
                    "strength": strength,
                    "hint": hint,
                    "suggested_risk_mode": suggested_risk_mode,
                    "diagnosis_summary": journal_diagnosis["summary"],
                    "positives": journal_diagnosis["positives"],
                    "warnings": journal_diagnosis["warnings"],
                    "mistakes": list(set(
                        journal_diagnosis["mistakes"] + detected_mistakes
                    )),
                    "mistake_types": list(set(
                        journal_diagnosis["mistake_types"] + detected_mistake_types
                    )),
                    "mistake_types": journal_diagnosis["mistake_types"],
                    "main_mistake": journal_diagnosis["main_mistake"],
                    "main_mistake_type": journal_diagnosis["main_mistake_type"],
                    "learning_step": journal_diagnosis["learning_step"],
                }

                st.session_state.confirm_trade = False
                st.session_state.active_page = "paper_trading"
                st.rerun()

        with c2:
            if st.button("❌ Abbrechen", use_container_width=True, key="confirm_trade_no"):
                st.session_state.confirm_trade = False
                st.rerun()

    # =====================================================
    # RAW DATA NUR IN ADVANCED
    # =====================================================
    if st.session_state.advanced_mode:
        with st.expander("Letzte Daten", expanded=False):
            cols_to_show = [
                c
                for c in [
                    "Open",
                    "High",
                    "Low",
                    "Close",
                    "Volume",
                    "EMA20",
                    "EMA50",
                    "EMA200",
                    "RSI",
                    "MACD",
                ]
                if c in data.columns
            ]
            st.dataframe(data[cols_to_show].tail(20), use_container_width=True)