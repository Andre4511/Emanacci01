import pandas as pd
import streamlit as st


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


def render_journal_page() -> None:
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

    df = pd.DataFrame(scored_journal)

    # Pflichtspalten absichern
    required_defaults = {
        "symbol": "-",
        "type": "-",
        "entry": 0.0,
        "exit": 0.0,
        "pnl": 0.0,
        "pnl_pct": 0.0,
        "setup_score": 0,
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

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Trades", int(trades_count))
    m2.metric("Winrate", f"{winrate:.1f}%")
    m3.metric("Ø PnL %", f"{avg_pnl_pct:.2f}%")
    m4.metric("Gesamt PnL", f"{total_pnl:.2f}")

    st.divider()

    # =====================================================
    # VISUELLE AUSWERTUNG
    # =====================================================
    st.subheader("Trade-Historie visuell")

    c1, c2 = st.columns(2)

    with c1:
        st.write("**PnL pro Trade**")
        pnl_chart_df = filtered_df.reset_index(drop=True).copy()
        pnl_chart_df.index = pnl_chart_df.index + 1
        st.bar_chart(pnl_chart_df[["pnl"]], width="stretch")

    with c2:
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
    # TABELLE
    # =====================================================
    st.subheader("Alle Trades")

    preferred_order = [
        "symbol",
        "entry",
        "exit",
        "pnl",
        "pnl_pct",
        "type",
        "setup_score",
    ]

    display_cols = [col for col in preferred_order if col in filtered_df.columns]

    st.dataframe(filtered_df[display_cols], width="stretch")