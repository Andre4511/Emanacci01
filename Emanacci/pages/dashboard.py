import streamlit as st
from utils import load_data
import plotly.graph_objects as go


def render_dashboard():

    if "watchlist" not in st.session_state:
        st.session_state.watchlist = ["TSLA", "AAPL", "NVDA"]
    
    st.title("Dashboard")

    ticker = st.session_state.get("ticker", "TSLA")
    watchlist = st.session_state.get("watchlist", ["TSLA", "AAPL", "NVDA"])

    st.subheader("Schnellüberblick")

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
        c2.metric("Kurs", f"{current_price:.2f}")
        c3.metric("Tagesänderung", f"{change_pct:.2f}%")

        st.info(f"Aktueller Marktstatus für **{ticker}**: **{market_status}**")

        if st.button("Zur Analyse", width="stretch"):
            st.session_state.active_page = "analyse"
            st.rerun()
    else:
        st.warning("Für das aktuelle Symbol konnten keine Daten geladen werden.")

    st.divider()
    st.subheader("Watchlist")

    new_symbol = st.text_input("Symbol zur Watchlist hinzufügen").upper().strip()

    if st.button("Hinzufügen", width="stretch"):
        if new_symbol and new_symbol not in st.session_state.watchlist:
            st.session_state.watchlist.append(new_symbol)
            st.success(f"{new_symbol} hinzugefügt")
            st.rerun()

    if watchlist:
        for symbol in watchlist:
            row1, row2, row3 = st.columns([2, 1, 1])

            symbol_data = load_data(symbol, "1mo", "1d")

            with row1:
                st.write(f"**{symbol}**")

            with row2:
                if st.button("Öffnen", key=f"open_{symbol}", width="stretch"):
                    st.session_state.ticker = symbol
                    st.session_state.active_page = "analyse"
                    st.rerun()

            with row3:
                if st.button("❌", key=f"delete_{symbol}"):
                    st.session_state.watchlist.remove(symbol)
                    st.rerun()

            if not symbol_data.empty:
                price = float(symbol_data["Close"].iloc[-1])
                prev = float(symbol_data["Close"].iloc[-2]) if len(symbol_data) > 1 else price
                change = ((price - prev) / prev * 100) if prev != 0 else 0.0

                st.caption(f"Kurs: {price:.2f} | Änderung: {change:.2f}%")

                mini_fig = create_mini_chart(symbol_data)
                st.plotly_chart(mini_fig, width="stretch")
            else:
                st.caption("Keine Daten verfügbar")

            st.divider()
    else:
        st.info("Deine Watchlist ist aktuell leer.")

def create_mini_chart(data):
    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=data.index,
            y=data["Close"],
            mode="lines",
            name="Close",
        )
    )

    fig.update_layout(
        height=90,
        margin=dict(l=0, r=0, t=0, b=0),
        xaxis_visible=False,
        yaxis_visible=False,
        showlegend=False,
    )

    return fig