# =========================================================
# WATCHLIST MIT MINI-CHARTS (schönere Karten)
# =========================================================

import streamlit as st
import plotly.graph_objects as go
from utils import load_data


def create_mini_chart(data):
    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=data.index,
            y=data["Close"],
            line=dict(color="#4FC3F7", width=2),
            name="Close",
        )
    )

    fig.update_layout(
        height=120,
        margin=dict(l=0, r=0, t=0, b=0),
        xaxis_visible=False,
        yaxis_visible=False,
        showlegend=False,
    )

    return fig


def render_watchlist():
    st.subheader("Watchlist")

    watchlist = st.session_state.get("watchlist", ["TSLA", "AAPL", "NVDA"])

    cols = st.columns(3)

    for i, symbol in enumerate(watchlist):
        with cols[i % 3]:
            data = load_data(symbol, "1mo", "1d")

            with st.container(border=True):
                if data.empty:
                    st.write(f"**{symbol}**")
                    st.caption("Keine Daten")
                    continue

                price = float(data["Close"].iloc[-1])
                prev = float(data["Close"].iloc[-2]) if len(data) > 1 else price
                change = (price - prev) / prev * 100 if prev != 0 else 0.0

                st.markdown(f"### {symbol}")
                st.write(f"**{price:.2f} USD**")
                st.caption(f"Tagesänderung: {change:.2f}%")

                fig = create_mini_chart(data)
                st.plotly_chart(fig, width="stretch")

                if st.button("Analysieren", key=f"watch_{symbol}", width="stretch"):
                    st.session_state.ticker = symbol
                    st.session_state.active_page = "analyse"
                    st.rerun()