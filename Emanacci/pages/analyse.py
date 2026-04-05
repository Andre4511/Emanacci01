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

    # =====================================================
    # TOP BAR
    # =====================================================
    col1, col2, col3, col4 = st.columns([2, 1, 1, 1])

    with col1:
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

        if st.button("⭐ Zur Watchlist hinzufügen", use_container_width=True, key="add_to_watchlist"):
            if "watchlist" not in st.session_state:
                st.session_state.watchlist = []

            if st.session_state.ticker not in st.session_state.watchlist:
                st.session_state.watchlist.append(st.session_state.ticker)
                st.success("Zur Watchlist hinzugefügt")
            else:
                st.info("Bereits in der Watchlist")

    with col2:
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

    with col3:
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

    with col4:
        st.write("")
        if st.button("Reload", use_container_width=True, key="analyse_reload"):
            st.rerun()

        st.toggle(
            "Advanced",
            value=st.session_state.advanced_mode,
            key="advanced_mode",
        )

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

    # =====================================================
    # ADVANCED SETTINGS
    # =====================================================
    if st.session_state.advanced_mode:
        with st.expander("Advanced Einstellungen", expanded=False):
            st.toggle("EMA anzeigen", key="show_ema")
            st.toggle("RSI anzeigen", key="show_rsi")
            st.toggle("Volumen anzeigen", key="show_volume")

    # =====================================================
    # MARKTEINSCHÄTZUNG
    # =====================================================
    st.markdown('<div class="em-section-card">', unsafe_allow_html=True)
    st.markdown('<div class="em-section-title">Markteinschätzung</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="em-section-sub">Einfache Einordnung für den aktuellen Markt</div>',
        unsafe_allow_html=True,
    )

    m1, m2, m3 = st.columns(3)
    m1.metric("Trend", trend)
    m2.metric("Stärke", strength)
    m3.metric("Status", hint)

    st.markdown("</div>", unsafe_allow_html=True)

    st.divider()

    # =====================================================
    # TRADE SETUP
    # =====================================================
    st.markdown('<div class="em-section-card">', unsafe_allow_html=True)
    st.markdown('<div class="em-section-title">Trade Setup</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="em-section-sub">Entry, Risiko und Ziele schnell planen</div>',
        unsafe_allow_html=True,
    )

    s1, s2, s3 = st.columns(3)

    with s1:
        entry = st.number_input(
            "Entry",
            value=float(latest_price),
            key="analyse_entry",
        )

    with s2:
        sl_percent = st.number_input(
            "Stop Loss %",
            value=2.0,
            min_value=0.1,
            step=0.1,
            key="analyse_sl_percent",
        )

    with s3:
        tp1_percent = st.number_input(
            "Take Profit 1 %",
            value=4.0,
            min_value=0.1,
            step=0.1,
            key="analyse_tp1_percent",
        )

    tp2_percent = st.number_input(
        "Take Profit 2 %",
        value=8.0,
        min_value=0.1,
        step=0.1,
        key="analyse_tp2_percent",
    )

    risk_amount = st.number_input(
        "Max. Risiko (€)",
        min_value=1.0,
        value=float(st.session_state.risk_amount_eur),
        step=10.0,
        key="analyse_risk_amount",
    )
    st.session_state.risk_amount_eur = float(risk_amount)

    sl_price = entry * (1 - sl_percent / 100)
    tp1_price = entry * (1 + tp1_percent / 100)
    tp2_price = entry * (1 + tp2_percent / 100)

    risk_per_share = entry - sl_price
    reward_per_share = tp1_price - entry
    rr = reward_per_share / risk_per_share if risk_per_share > 0 else 0.0
    position_size = risk_amount / risk_per_share if risk_per_share > 0 else 0.0

    r1, r2, r3, r4, r5 = st.columns(5)
    r1.metric("SL Preis", f"{sl_price:.2f}")
    r2.metric("TP1 Preis", f"{tp1_price:.2f}")
    r3.metric("TP2 Preis", f"{tp2_price:.2f}")
    r4.metric("RR", f"{rr:.2f}")
    r5.metric("Empfohlene Stückzahl", f"{position_size:.2f}")

    st.markdown("</div>", unsafe_allow_html=True)

    st.divider()

    # =====================================================
    # CHART
    # =====================================================
    st.subheader("Chart")

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
    # SIMPLE / ADVANCED INFO
    # =====================================================
    if not st.session_state.advanced_mode:
        st.info(hint)
    else:
        st.write(f"Trend: {trend}")
        st.write(f"Stärke: {strength}")
        st.info(hint)

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