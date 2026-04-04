import streamlit as st
from utils import load_data
import plotly.graph_objects as go


def render_dashboard():

    if "watchlist" not in st.session_state:
        st.session_state.watchlist = ["TSLA", "AAPL", "NVDA"]
    
    st.title("Dashboard")

    ticker = st.session_state.get("ticker", "TSLA")
    watchlist = st.session_state.get("watchlist", ["TSLA", "AAPL", "NVDA"])

    st.markdown('<div class="em-section-card">', unsafe_allow_html=True)
    st.markdown('<div class="em-section-title">Schnellüberblick</div>', unsafe_allow_html=True)
    st.markdown('<div class="em-section-sub">Dein aktuelles Symbol auf einen Blick</div>', unsafe_allow_html=True)

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

    st.markdown('</div>', unsafe_allow_html=True)

    st.divider()

    st.markdown('<div class="em-section-card">', unsafe_allow_html=True)
    st.markdown('<div class="em-section-title">Watchlist</div>', unsafe_allow_html=True)
    st.markdown('<div class="em-section-sub">Deine beobachteten Werte mit Schnellzugriff</div>', unsafe_allow_html=True)

    st.subheader("Watchlist")

    new_symbol = st.text_input("Symbol zur Watchlist hinzufügen").upper().strip()

    if st.button("Hinzufügen", width="stretch"):
        if new_symbol and new_symbol not in st.session_state.watchlist:
            st.session_state.watchlist.append(new_symbol)
            st.success(f"{new_symbol} hinzugefügt")
            st.rerun()

    watchlist = st.session_state.get("watchlist", [])

    if watchlist:
        cols = st.columns(3)

        for i, symbol in enumerate(watchlist):
            with cols[i % 3]:
                symbol_data = load_data(symbol, "1mo", "1d")

                with st.container(border=True):
                    top_left, top_right = st.columns([4, 1])

                    with top_left:
                        if not symbol_data.empty:
                            price = float(symbol_data["Close"].iloc[-1])
                            prev = float(symbol_data["Close"].iloc[-2]) if len(symbol_data) > 1 else price
                            change = ((price - prev) / prev * 100) if prev != 0 else 0.0

                            if st.button(f"{symbol}", key=f"open_{symbol}", use_container_width=True):
                                st.session_state.ticker = symbol
                                st.session_state.active_page = "analyse"
                                st.rerun()

                            st.caption(f"{price:.2f} USD | {change:.2f}%")
                        else:
                            if st.button(f"{symbol}", key=f"open_{symbol}", use_container_width=True):
                                st.session_state.ticker = symbol
                                st.session_state.active_page = "analyse"
                                st.rerun()

                            st.caption("Keine Daten verfügbar")

                    with top_right:
                        if st.button("✕", key=f"delete_{symbol}"):
                            st.session_state.watchlist.remove(symbol)
                            st.rerun()

                    if not symbol_data.empty:
                        mini_fig = create_mini_chart(symbol_data)
                        st.plotly_chart(mini_fig, width="stretch")

    else:
        st.info("Deine Watchlist ist aktuell leer.")

    st.markdown('</div>', unsafe_allow_html=True)

def create_mini_chart(data):
    import plotly.graph_objects as go

    close = data["Close"].astype(float)

    price_now = float(close.iloc[-1])
    price_start = float(close.iloc[0])
    is_up = price_now >= price_start

    line_color = "#00E676" if is_up else "#FF5252"
    glow_color_1 = "rgba(0,230,118,0.16)" if is_up else "rgba(255,82,82,0.16)"
    glow_color_2 = "rgba(0,230,118,0.06)" if is_up else "rgba(255,82,82,0.06)"

    ymin = float(close.min())
    ymax = float(close.max())
    padding = (ymax - ymin) * 0.25 if ymax > ymin else ymax * 0.01 if ymax != 0 else 1
    lower_band_1 = close - padding * 0.55
    lower_band_2 = close - padding

    fig = go.Figure()

    # Hauptlinie
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

    # erster Glow direkt unter der Linie
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

    # zweiter, transparenterer Glow
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