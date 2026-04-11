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
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def _get_period_interval() -> tuple[str, str]:
    zoom_map = {
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

    st.caption("Wähle zuerst eine Aktie und einen Zeitraum. Danach bekommst du eine einfache Einschätzung.")

    # =====================================================
    # TOP BAR / STEUERUNG
    # =====================================================
    ticker_input = st.text_input(
        "Symbol",
        value=st.session_state.ticker,
        key="analyse_ticker_input",
    ).upper().strip()

    if ticker_input:
        st.session_state.ticker = ticker_input

    active_zoom = st.session_state.zoom
    z1, z2, z3, z4, z5 = st.columns(5)

    def zoom_button(label: str, key: str) -> bool:
        is_active = active_zoom == label
        return st.button(
            label,
            key=key,
            use_container_width=True,
            type="primary" if is_active else "secondary",
        )

    with z1:
        if zoom_button("1W", "zoom_1w"):
            st.session_state.zoom = "1W"
            st.rerun()

    with z2:
        if zoom_button("1M", "zoom_1m"):
            st.session_state.zoom = "1M"
            st.rerun()

    with z3:
        if zoom_button("3M", "zoom_3m"):
            st.session_state.zoom = "3M"
            st.rerun()

    with z4:
        if zoom_button("6M", "zoom_6m"):
            st.session_state.zoom = "6M"
            st.rerun()

    with z5:
        if zoom_button("1Y", "zoom_1y"):
            st.session_state.zoom = "1Y"
            st.rerun()

    st.caption(f"Aktueller Zoom: {st.session_state.zoom}")

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
    data = data.tail(300)

    if data.empty:
        st.warning("Keine Daten gefunden.")
        st.stop()

    data = calculate_indicators(data)

    latest_rsi = data["RSI"].iloc[-1] if "RSI" in data.columns else None
    latest_ema20 = data["EMA20"].iloc[-1] if "EMA20" in data.columns else None
    latest_ema50 = data["EMA50"].iloc[-1] if "EMA50" in data.columns else None
    latest_price = float(data["Close"].iloc[-1])

    trend = "-"
    strength = "-"
    hint = "-"

    if latest_ema20 is not None and latest_ema50 is not None:
        trend = "Bullisch" if latest_ema20 > latest_ema50 else "Bärisch"

    if latest_rsi is not None:
        if latest_rsi > 60:
            strength = "Stark"
        elif latest_rsi < 40:
            strength = "Schwach"
        else:
            strength = "Neutral"

    if trend == "Bullisch" and strength == "Stark":
        hint = "Trend läuft sauber nach oben"
    elif trend == "Bärisch" and strength == "Stark":
        hint = "Abwärtstrend dominant"
    else:
        hint = "Markt eher neutral"

    signal = "Neutral"
    risk = "Mittel"
    action = "Beobachten"
    color = "yellow"

    # =====================================================
    # CHART KOMMENTARE (NEU)
    # =====================================================

    chart_comments = []

    # EMA Bewertung
    if latest_ema20 and latest_ema50:
        if latest_price > latest_ema20 > latest_ema50:
            chart_comments.append("Trend wirkt stabil nach oben (über EMA).")
        elif latest_price < latest_ema20 < latest_ema50:
            chart_comments.append("Abwärtstrend intakt (unter EMA).")
        else:
            chart_comments.append("Trend nicht klar – EMA Linien gemischt.")

    # RSI Bewertung
    if latest_rsi:
        if latest_rsi > 70:
            chart_comments.append("RSI hoch – Markt könnte überkauft sein.")
        elif latest_rsi < 30:
            chart_comments.append("RSI niedrig – mögliche Gegenbewegung.")
        else:
            chart_comments.append("RSI im normalen Bereich.")

    # Einstiegssignal
    if signal == "Unklar":
        chart_comments.append("Noch kein klares Einstiegssignal.")
    elif signal == "Positiv":
        chart_comments.append("Mögliches Einstiegssignal vorhanden – Bestätigung abwarten.")
    elif signal == "Negativ":
        chart_comments.append("Signal eher negativ – Vorsicht.")

    # =====================================================
    # KLARTEXT-ZUSAMMENFASSUNG (NEU)
    # =====================================================

    summary_text = ""

    if signal == "Positiv" and trend == "Bullisch":
        summary_text = "Trend stabil, aber Einstieg sollte bestätigt werden."
    elif signal == "Negativ":
        summary_text = "Aktuell kein guter Einstieg – Risiko eher hoch."
    elif signal == "Unklar":
        summary_text = "Noch kein klares Signal – lieber beobachten."
    else:
        summary_text = "Markt aktuell gemischt – vorsichtig bleiben."

    # Handlung klarer formulieren
    action_text = action

    if signal == "Unklar":
        action_text = "Warte auf eine klare Bestätigung."
    elif signal == "Positiv":
        action_text = "Beobachten oder kleiner Einstieg möglich."
    elif signal == "Negativ":
        action_text = "Lieber nicht einsteigen."

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
    elif strength == "Neutral":
        signal = "Unklar"
        risk = "Mittel"
        action = "Auf klares Signal warten"
        color = "yellow"

    # =====================================================
    # ADVANCED SETTINGS
    # =====================================================
    if st.session_state.advanced_mode:
        with st.expander("Advanced Einstellungen", expanded=False):
            st.toggle("EMA anzeigen", key="show_ema")
            st.toggle("RSI anzeigen", key="show_rsi")
            st.toggle("Volumen anzeigen", key="show_volume")

    # =====================================================
    # TOP ZUSAMMENFASSUNG (ANFÄNGER)
    # =====================================================
    st.markdown('<div class="em-section-card">', unsafe_allow_html=True)
    st.markdown('<div class="em-section-title">Schnelle Einschätzung</div>', unsafe_allow_html=True)

    # KLARTEXT (NEU – GANZ OBEN)
    st.markdown(f"### {summary_text}")

    # AMPEL
    if color == "green":
        st.success(f"🟢 {action_text}")
    elif color == "red":
        st.error(f"🔴 {action_text}")
    else:
        st.warning(f"🟡 {action_text}")

    # METRICS
    c1, c2, c3 = st.columns(3)
    c1.metric("Signal", signal)
    c2.metric("Risiko", risk)
    c3.metric("Trend", trend)

    # KURZE ERKLÄRUNG
    st.caption(hint)

    # =====================================================
    # STANDARDWERTE FÜR CHART UND TRADE SETUP
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
    # CHART
    # =====================================================
    st.subheader("Chart – aktueller Verlauf")

    if not st.session_state.advanced_mode:
        fig = create_main_chart(
            data,
            show_ema=True,
            show_volume=True,
            show_rsi=False,
            entry=entry,
            stop_loss=sl_price,
            tp1=tp1_price,
            tp2=tp2_price,
            qty=position_size,
            risk_amount=risk_amount,
        )
    else:
        fig = create_main_chart(
            data,
            show_ema=st.session_state.show_ema,
            show_volume=st.session_state.show_volume,
            show_rsi=st.session_state.show_rsi,
            entry=entry,
            stop_loss=sl_price,
            tp1=tp1_price,
            tp2=tp2_price,
            qty=position_size,
            risk_amount=risk_amount,
        )

    st.plotly_chart(
        fig,
        width="stretch",
        config={
            "displaylogo": False,
            "scrollZoom": True,
            "modeBarButtonsToRemove": [
                "select2d",
                "lasso2d",
                "autoScale2d",
            ],
        },
    )

    # =====================================================
    # CHART KOMMENTARE ANZEIGEN
    # =====================================================

    st.markdown("### Was im Chart passiert")

    for comment in chart_comments:
        st.write(f"- {comment}")

    # =====================================================
    # MARKTEINSCHÄTZUNG
    # =====================================================
    st.markdown('<div class="em-section-card">', unsafe_allow_html=True)
    st.markdown('<div class="em-section-title">Markteinschätzung</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="em-section-sub">Einfache Einordnung für den aktuellen Markt</div>',
        unsafe_allow_html=True,
    )

    if not st.session_state.advanced_mode:
        st.write(f"**Trend:** {trend}")
        st.write(f"**Stärke:** {strength}")
        st.write(f"**Signal:** {signal}")
    else:
        m1, m2, m3 = st.columns(3)
        m1.metric("Trend", trend)
        m2.metric("Stärke", strength)
        m3.metric("Signal", signal)

    st.markdown("</div>", unsafe_allow_html=True)
    st.divider()

    # =====================================================
    # DIAGNOSE
    # =====================================================
    positives = []
    warnings = []
    learning_step = "Achte weiter auf Trend, Risiko und klare Bestätigung."
    mistakes = []

    if trend == "Bullisch":
        positives.append("Der Trend zeigt nach oben.")
    elif trend == "Bärisch":
        warnings.append("Der Trend zeigt aktuell nach unten.")

    if strength == "Stark":
        positives.append("Die aktuelle Bewegung ist relativ stark.")
    elif strength == "Schwach":
        warnings.append("Die Bewegung wirkt eher schwach.")

    if signal == "Positiv":
        positives.append("Das Signal ist eher positiv.")
    elif signal == "Unklar":
        warnings.append("Das Signal ist noch nicht klar genug.")
    elif signal == "Negativ":
        warnings.append("Das Signal wirkt aktuell negativ.")

    if rr < 1.5:
        warnings.append("Das Chance-Risiko-Verhältnis ist eher schwach.")
        learning_step = "Lerne, wie du Einstieg, Stop-Loss und Ziele besser zueinander planst."
    elif rr >= 2.0:
        positives.append("Das Chance-Risiko-Verhältnis wirkt solide.")

    if risk == "Hoch":
        warnings.append("Das Risiko ist aktuell hoch.")
        learning_step = "Prüfe, wie du Risiko reduzieren oder auf bessere Bestätigung warten kannst."

    if trend == "Bullisch" and signal == "Unklar":
        warnings.append("Der Trend ist zwar positiv, aber der Einstieg ist noch nicht sauber bestätigt.")
        learning_step = "Lerne, wie eine Bestätigung vor dem Einstieg aussehen kann."

    if trend == "Bärisch" and signal == "Negativ":
        warnings.append("Ein Einstieg wäre hier für Anfänger eher riskant.")
        learning_step = "Lerne zuerst, wie Abwärtstrends und Gegenbewegungen unterschieden werden."

    if signal == "Unklar":
        mistakes.append("Zu früher Einstieg (Signal nicht bestätigt)")

    if rr < 1.5:
        mistakes.append("Schlechtes Chance-Risiko-Verhältnis")

    if trend == "Bärisch":
        mistakes.append("Gegen den Trend handeln")

    if risk == "Hoch":
        mistakes.append("Zu hohes Risiko")

    if trend == "Bullisch" and strength == "Schwach":
        mistakes.append("Schwacher Trend – Einstieg unsicher")

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
        "Schwacher Trend – Einstieg unsicher": "Der Markt bewegt sich, aber ohne klare Stärke.",
    }

    mistake_types = {
        "Zu früher Einstieg (Signal nicht bestätigt)": "Timing-Fehler",
        "Schlechtes Chance-Risiko-Verhältnis": "Risiko-Fehler",
        "Gegen den Trend handeln": "Trend-Fehler",
        "Zu hohes Risiko": "Risiko-Fehler",
        "Schwacher Trend – Einstieg unsicher": "Trend-Fehler",
    }

    mistake_priority = {
        "Gegen den Trend handeln": 1,
        "Zu hohes Risiko": 1,
        "Zu früher Einstieg (Signal nicht bestätigt)": 2,
        "Schlechtes Chance-Risiko-Verhältnis": 3,
        "Schwacher Trend – Einstieg unsicher": 4,
    }

    if mistakes:
        mistakes = sorted(mistakes, key=lambda m: mistake_priority.get(m, 99))

    st.markdown('<div class="em-section-card">', unsafe_allow_html=True)
    st.markdown('<div class="em-section-title">Diagnose</div>', unsafe_allow_html=True)
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

        if len(mistakes) > 1:
            st.markdown("Weitere Punkte:")
            for m in mistakes[1:]:
                m_type = mistake_types.get(m, "Fehler")
                st.write(f"- {m}")
                st.caption(f"Typ: {m_type}")
                if m in mistake_explanations:
                    st.caption(mistake_explanations[m])

    st.markdown("### 🟡 Nächster Schritt")
    st.write(learning_step)
    st.caption(f"Aktuelles Risiko: {risk}")

    st.markdown("</div>", unsafe_allow_html=True)
    st.divider()

    # =====================================================
    # ANFÄNGER ERKLÄRUNG
    # =====================================================
    st.markdown('<div class="em-section-card">', unsafe_allow_html=True)
    st.markdown('<div class="em-section-title">Was passiert gerade?</div>', unsafe_allow_html=True)

    explanation = ""

    if trend == "Bullisch":
        explanation += "Der Trend zeigt nach oben. "
    elif trend == "Bärisch":
        explanation += "Der Trend zeigt nach unten. "
    else:
        explanation += "Der Markt hat aktuell keinen klaren Trend. "

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
    st.markdown('<div class="em-section-title">Was kannst du jetzt tun?</div>', unsafe_allow_html=True)

    st.write(f"👉 {action}")

    if signal == "Unklar":
        st.write("Warte auf eine klarere Bewegung oder Bestätigung.")
    elif signal == "Positiv":
        st.write("Du kannst den Markt beobachten oder vorsichtig einsteigen.")
    elif signal == "Negativ":
        st.write("Lieber abwarten oder Risiko reduzieren.")

    st.markdown("</div>", unsafe_allow_html=True)

    # =====================================================
    # LERNHINWEISE (ANFÄNGER)
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

        r1, r2 = st.columns(2)
        r1.metric("Stop-Loss Preis", f"{sl_price:.2f}")
        r2.metric("Take-Profit 1", f"{tp1_price:.2f}")

        r3, r4, r5 = st.columns(3)
        r3.metric("Take-Profit 2", f"{tp2_price:.2f}")
        r4.metric("Chance/Risiko", f"{rr:.2f}")
        r5.metric("Stückzahl", f"{position_size:.2f}")

        if rr < 1.5:
            st.warning("Das Chance-Risiko-Verhältnis ist eher schwach.")
        elif rr >= 2.0:
            st.success("Das Chance-Risiko-Verhältnis wirkt solide.")
        else:
            st.info("Das Chance-Risiko-Verhältnis ist okay, aber nicht stark.")

        if not st.session_state.advanced_mode and signal == "Unklar":
            st.warning("Für Anfänger ist ein Einstieg bei unklarem Signal meist keine gute Idee.")

        if not st.session_state.advanced_mode and trend == "Bärisch":
            st.warning("Für Anfänger ist ein Einstieg gegen einen fallenden Trend oft riskant.")

        st.markdown("</div>", unsafe_allow_html=True)

    st.divider()

    # =====================================================
    # SIMPLE / ADVANCED INFO
    # =====================================================
    if not st.session_state.advanced_mode:
        st.info(f"{action} – {hint}")
        st.caption("Tipp: Achte zuerst auf Trend, Risiko und klare Bestätigung. Nicht jeder laufende Kurs ist ein guter Einstieg.")
    else:
        st.write(f"Trend: {trend}")
        st.write(f"Stärke: {strength}")
        st.write(f"Signal: {signal}")
        st.write(f"Risiko: {risk}")
        st.info(hint)

    # =====================================================
    # JOURNAL-DATEN VORBEREITEN
    # =====================================================
    journal_mistake_types = [
        mistake_types.get(m, "Fehler")
        for m in mistakes
    ]

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
    # ACTION
    # =====================================================
    if st.button("🚀 Trade in Paper Trading übernehmen", use_container_width=True, key="analyse_to_paper"):
        st.session_state.paper_trade_idea = {
            "symbol": st.session_state.ticker,
            "entry": float(entry),
            "stop_loss": float(sl_price),
            "take_profit_1": float(tp1_price),
            "take_profit_2": float(tp2_price),
            "rr": float(rr),
            "suggested_qty": float(position_size),
            "risk_amount_eur": float(risk_amount),

            "signal": signal,
            "risk": risk,
            "trend": trend,
            "strength": strength,
            "hint": hint,
            "diagnosis_summary": journal_diagnosis["summary"],
            "positives": journal_diagnosis["positives"],
            "warnings": journal_diagnosis["warnings"],
            "mistakes": journal_diagnosis["mistakes"],
            "mistake_types": journal_diagnosis["mistake_types"],
            "main_mistake": journal_diagnosis["main_mistake"],
            "main_mistake_type": journal_diagnosis["main_mistake_type"],
            "learning_step": journal_diagnosis["learning_step"],
        }

        st.session_state.active_page = "paper_trading"
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
            st.dataframe(data[cols_to_show].tail(20), width="stretch")