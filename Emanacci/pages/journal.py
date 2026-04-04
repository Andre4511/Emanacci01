import pandas as pd
import streamlit as st


def get_setup_score(trade):
    score = 0

    pnl_pct = trade.get("pnl_pct", 0)
    trade_type = trade.get("type", "")

    if pnl_pct > 0:
        score += 2
    if pnl_pct >= 2:
        score += 1
    if trade_type == "TP":
        score += 2
    if trade_type == "MANUAL":
        score -= 1
    if trade_type == "SL":
        score -= 2

    return score


def render_journal_page():
    st.title("Journal")

    journal = st.session_state.get("trade_journal", [])

    if not journal:
        st.info("Noch keine Trades vorhanden.")
        return

    scored_journal = []
    for trade in journal:
        trade_copy = trade.copy()
        trade_copy["setup_score"] = get_setup_score(trade)
        scored_journal.append(trade_copy)

    # =====================================================
    # DATAFRAME
    # =====================================================
    df = pd.DataFrame(scored_journal)

    if "symbol" not in df.columns:
        df["symbol"] = "-"
    if "type" not in df.columns:
        df["type"] = "-"
    if "pnl" not in df.columns:
        df["pnl"] = 0.0
    if "pnl_pct" not in df.columns:
        df["pnl_pct"] = 0.0
    if "entry" not in df.columns:
        df["entry"] = 0.0
    if "exit" not in df.columns:
        df["exit"] = 0.0

    # =====================================================
    # FILTER
    # =====================================================
    st.subheader("Filter")

    filter_col1, filter_col2 = st.columns(2)

    with filter_col1:
        symbol_options = ["Alle"] + sorted(df["symbol"].dropna().astype(str).unique().tolist())
        selected_symbol = st.selectbox("Symbol", symbol_options)

    with filter_col2:
        type_options = ["Alle", "TP", "SL", "MANUAL", "PARTIAL"]
        selected_type = st.selectbox("Typ", type_options)

    filtered_df = df.copy()

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
    avg_pnl_pct = filtered_df["pnl_pct"].mean() if trades_count > 0 else 0.0
    total_pnl = filtered_df["pnl"].sum() if trades_count > 0 else 0.0

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Trades", int(trades_count))
    m2.metric("Winrate", f"{winrate:.1f}%")
    m3.metric("Ø PnL %", f"{avg_pnl_pct:.2f}%")
    m4.metric("Gesamt PnL", f"{total_pnl:.2f}")

    # =====================================================
    # CHARTS
    # =====================================================
    st.divider()
    st.subheader("Trade-Historie visuell")

    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        st.write("**PnL pro Trade**")
        pnl_chart_df = filtered_df.reset_index(drop=True).copy()
        pnl_chart_df.index = pnl_chart_df.index + 1
        pnl_chart_df = pnl_chart_df[["pnl"]]
        st.bar_chart(pnl_chart_df, width="stretch")

    with chart_col2:
        st.write("**Gewinner vs Verlierer**")
        wl_df = pd.DataFrame({
            "Anzahl": [len(wins_df), len(losses_df)]
        }, index=["Gewinner", "Verlierer"])
        st.bar_chart(wl_df, width="stretch")

    # =====================================================
    # BESTE / SCHWÄCHSTE TRADES
    # =====================================================
    st.divider()
    st.subheader("Pro Trade Analyse")

    best_trades = filtered_df.sort_values("setup_score", ascending=False).head(5)
    worst_trades = filtered_df.sort_values("setup_score", ascending=True).head(5)

    b1, b2 = st.columns(2)

    with b1:
        st.write("**Beste Trades**")
        st.dataframe(best_trades, width="stretch")

    with b2:
        st.write("**Schwächste Trades**")
        st.dataframe(worst_trades, width="stretch")

    # =====================================================
    # AUSWERTUNG
    # =====================================================
    st.divider()
    st.subheader("Auswertung")

    types = filtered_df["type"].astype(str).tolist()
    most_common_type = max(set(types), key=types.count) if types else None

    if most_common_type == "SL":
        st.warning("Du wirst häufig ausgestoppt → Stop Loss evtl. zu eng oder Einstieg zu früh.")
    elif most_common_type == "TP":
        st.success("Viele Trades erreichen Take Profit → Strategie wirkt solide.")
    elif most_common_type == "MANUAL":
        st.info("Viele Trades werden manuell geschlossen → evtl. Emotionen im Spiel.")

    st.write(f"Ø Ergebnis: {avg_pnl_pct:.2f}%")

    # =====================================================
    # TABELLE
    # =====================================================
    st.divider()
    st.subheader("Alle Trades")

    display_cols = [c for c in ["symbol", "entry", "exit", "pnl", "pnl_pct", "type", "setup_score"] if c in filtered_df.columns]
    st.dataframe(filtered_df[display_cols], width="stretch")
