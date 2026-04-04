import streamlit as st

from indicators import calculate_indicators
from utils import load_data
from components.charts import create_main_chart


def render_analyse_page():
    if "ticker" not in st.session_state:
        st.session_state.ticker = "TSLA"

    if "period" not in st.session_state:
        st.session_state.period = "6mo"

    if "interval" not in st.session_state:
        st.session_state.interval = "1d"

    if "show_volume" not in st.session_state:
        st.session_state.show_volume = True

    if "show_rsi" not in st.session_state:
        st.session_state.show_rsi = True

    if "show_ema" not in st.session_state:
        st.session_state.show_ema = True

    if "risk_amount_eur" not in st.session_state:
        st.session_state.risk_amount_eur = 100.0

    if "use_tp2" not in st.session_state:
        st.session_state.use_tp2 = True

    if "show_raw_data" not in st.session_state:
        st.session_state.show_raw_data = False

    st.title("Analyse")

    col1, col2, col3, col4 = st.columns([2, 1, 1, 1])

    with col1:
        ticker_input = st.text_input("Symbol", value=st.session_state.ticker).upper().strip()

        if st.button("⭐ Zur Watchlist hinzufügen", width="stretch"):
            if "watchlist" not in st.session_state:
                st.session_state.watchlist = []

            if st.session_state.ticker not in st.session_state.watchlist:
                st.session_state.watchlist.append(st.session_state.ticker)
                st.success("Zur Watchlist hinzugefügt")

            else:
                st.info("Bereits in der Watchlist")
                
        if ticker_input:
            st.session_state.ticker = ticker_input

    with col2:
        period_options = ["5d", "1mo", "3mo", "6mo", "1y"]
        current_period = st.session_state.period if st.session_state.period in period_options else "6mo"
        st.session_state.period = st.selectbox("Zeitraum", period_options, index=period_options.index(current_period))

    with col3:
        interval_options = ["15m", "1h", "1d"]
        current_interval = st.session_state.interval if st.session_state.interval in interval_options else "1d"
        st.session_state.interval = st.selectbox("Intervall", interval_options, index=interval_options.index(current_interval))

    with col4:
        st.write("")
        if st.button("Reload", width="stretch"):
            st.rerun()

    st.divider()

    data = load_data(
        st.session_state.ticker,
        st.session_state.period,
        st.session_state.interval,
    )

    if data.empty:
        st.warning("Keine Daten gefunden.")
        st.stop()

    data = calculate_indicators(data)
    

    st.subheader("Chart")

    c1, c2, c3 = st.columns(3)

    with c1:
        st.session_state.show_ema = st.toggle("EMA", value=st.session_state.show_ema)

    with c2:
        st.session_state.show_volume = st.toggle("Volumen", value=st.session_state.show_volume)

    with c3:
        st.session_state.show_rsi = st.toggle("RSI", value=st.session_state.show_rsi)

    fig = create_main_chart(
        data,
        show_ema=st.session_state.show_ema,
        show_volume=st.session_state.show_volume,
        show_rsi=st.session_state.show_rsi,
    )

    st.plotly_chart(fig, width="stretch")

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

    st.divider()
    st.subheader("Markteinschätzung")

    m1, m2, m3 = st.columns(3)
    m1.metric("Trend", trend)
    m2.metric("Stärke", strength)
    m3.metric("Status", hint)

    st.divider()
    st.subheader("Trade Setup")

    with st.expander("Advanced Einstellungen"):
        st.session_state.show_ema = st.toggle(
            "EMA anzeigen",
            value=st.session_state.show_ema,
            key="analyse_show_ema"
        )

        st.session_state.show_volume = st.toggle(
            "Volumen anzeigen",
            value=st.session_state.show_volume,
            key="analyse_show_volume"
        )

        st.session_state.show_rsi = st.toggle(
            "RSI anzeigen",
            value=st.session_state.show_rsi,
            key="analyse_show_rsi"
        )

        st.session_state.use_tp2 = st.toggle(
            "TP2 verwenden",
            value=st.session_state.use_tp2,
            key="analyse_use_tp2"
        )

        st.session_state.show_raw_data = st.toggle(
            "Rohdaten anzeigen",
            value=st.session_state.show_raw_data,
            key="analyse_show_raw_data"
        )

    s1, s2, s3 = st.columns(3)

    with s1:
        entry = st.number_input("Entry", value=latest_price)

    with s2:
        sl_percent = st.number_input("Stop Loss %", value=2.0, min_value=0.1, step=0.1)

    with s3:
        tp1_percent = st.number_input("Take Profit 1 %", value=4.0, min_value=0.1, step=0.1)
        tp2_percent = st.number_input("Take Profit 2 %", value=8.0, min_value=0.1, step=0.1)

    sl_price = entry * (1 - sl_percent / 100)

    tp1_price = entry * (1 + tp1_percent / 100)

    if st.session_state.use_tp2:
        tp2_price = entry * (1 + tp2_percent / 100)
    else:
        tp2_price = tp1_price

    risk_per_share = entry - sl_price
    reward_per_share = tp1_price - entry

    rr = reward_per_share / risk_per_share if risk_per_share > 0 else 0.0

    st.session_state.risk_amount_eur = st.number_input(
        "Max. Risiko in €",
        min_value=1.0,
        value=float(st.session_state.risk_amount_eur),
        step=10.0,
    )

    if risk_per_share > 0:
        suggested_qty = st.session_state.risk_amount_eur / risk_per_share
    else:
        suggested_qty = 0.0

    estimated_position_size = entry * suggested_qty

    r1, r2, r3, r4, r5 = st.columns(5)
    r1.metric("SL Preis", f"{sl_price:.2f}")
    r2.metric("TP1 Preis", f"{tp1_price:.2f}")
    r3.metric("TP2 Preis", f"{tp2_price:.2f}")
    r4.metric("RR", f"{rr:.2f}")
    r5.metric("Vorschlag Stückzahl", f"{suggested_qty:.2f}")

    st.caption(f"Geschätzte Positionsgröße: {estimated_position_size:.2f}")

    if st.button("➡️ In Paper Trading übernehmen", width="stretch"):
        st.session_state.paper_trade_idea = {
            "symbol": st.session_state.ticker,
            "entry": float(entry),
            "stop_loss": float(sl_price),
            "take_profit_1": float(tp1_price),
            "take_profit_2": float(tp2_price),
            "rr": float(rr),
            "suggested_qty": float(suggested_qty),
            "risk_amount_eur": float(st.session_state.risk_amount_eur),
        }
        st.session_state.active_page = "paper_trading"
        st.rerun()

    if st.session_state.show_raw_data:
        with st.expander("Letzte Daten", expanded=False):
            cols_to_show = [
                c for c in
                ["Open", "High", "Low", "Close", "Volume", "EMA20", "EMA50", "EMA200", "RSI", "MACD"]
                if c in data.columns
            ]
            st.dataframe(data[cols_to_show].tail(20), width="stretch")