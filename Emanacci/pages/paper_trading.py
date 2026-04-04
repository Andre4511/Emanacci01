import streamlit as st
from utils import load_data


def render_paper_trading_page():
    # =====================================================
    # STATE
    # =====================================================
    if "paper_trade_idea" not in st.session_state:
        st.session_state.paper_trade_idea = None

    if "paper_positions" not in st.session_state:
        st.session_state.paper_positions = []

    if "paper_cash" not in st.session_state:
        st.session_state.paper_cash = 10000.0

    if "paper_trade_history" not in st.session_state:
        st.session_state.paper_trade_history = []

    if "trade_journal" not in st.session_state:
        st.session_state.trade_journal = []

    if "equity_curve" not in st.session_state:
        st.session_state.equity_curve = []

    if "paper_peak_equity" not in st.session_state:
        st.session_state.paper_peak_equity = 0.0

    start_capital = 10000.0

    if "max_portfolio_risk_eur" not in st.session_state:
        st.session_state.max_portfolio_risk_eur = 500.0

    if "trailing_stop_percent" not in st.session_state:
        st.session_state.trailing_stop_percent = 2.0

    if "use_break_even" not in st.session_state:
        st.session_state.use_break_even = True

    if "use_trailing_stop" not in st.session_state:
        st.session_state.use_trailing_stop = True

    if "use_tp1" not in st.session_state:
        st.session_state.use_tp1 = True

    st.title("Paper Trading")

    trade = st.session_state.paper_trade_idea
    positions = st.session_state.paper_positions

    # =====================================================
    # EQUITY ÜBER ALLE POSITIONEN
    # =====================================================
    total_open_value = 0.0

    for pos in positions:
        data = load_data(pos["symbol"], "5d", "1d")
        if not data.empty:
            current_price = float(data["Close"].iloc[-1])
        else:
            current_price = float(pos["entry"])

        total_open_value += current_price * float(pos["qty"])

    equity = st.session_state.paper_cash + total_open_value
    st.session_state.equity_curve.append(equity)

    if equity > st.session_state.paper_peak_equity:
        st.session_state.paper_peak_equity = equity

    peak_equity = st.session_state.paper_peak_equity
    drawdown_pct = ((equity - peak_equity) / peak_equity * 100) if peak_equity > 0 else 0.0
    performance_pct = ((equity - start_capital) / start_capital * 100) if start_capital > 0 else 0.0

    # =====================================================
    # KONTO
    # =====================================================
    st.subheader("Konto")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Cash", f"{st.session_state.paper_cash:.2f}")
    c2.metric("Equity", f"{equity:.2f}")
    c3.metric("Performance", f"{performance_pct:.2f}%")
    c4.metric("Drawdown", f"{drawdown_pct:.2f}%")

    st.divider()

    st.subheader("Portfolio Überblick")

    positions = st.session_state.paper_positions

    if positions:
        pnl_values = []

        for pos in positions:
            data = load_data(pos["symbol"], "5d", "1d")

            if not data.empty:
                current_price = float(data["Close"].iloc[-1])
            else:
                current_price = float(pos["entry"])

            pnl_abs = (current_price - float(pos["entry"])) * float(pos["qty"])
            pnl_values.append({
                "symbol": pos["symbol"],
                "pnl": pnl_abs
            })

        best_trade = max(pnl_values, key=lambda x: x["pnl"])
        worst_trade = min(pnl_values, key=lambda x: x["pnl"])

        p1, p2, p3 = st.columns(3)

        with p1:
            st.metric("Offene Positionen", len(positions))

        with p2:
            st.metric("Bester Trade", f"{best_trade['symbol']} ({best_trade['pnl']:.2f})")

        with p3:
            st.metric("Schwächster Trade", f"{worst_trade['symbol']} ({worst_trade['pnl']:.2f})")
    else:
        st.info("Noch kein Portfolio aufgebaut.")

    with st.expander("Advanced Einstellungen"):
        st.session_state.use_break_even = st.toggle(
            "Break-Even nach Teilverkauf",
            value=st.session_state.use_break_even,
        )

        st.session_state.use_trailing_stop = st.toggle(
            "Trailing Stop aktiv",
            value=st.session_state.use_trailing_stop,
        )

        st.session_state.trailing_stop_percent = st.number_input(
            "Trailing Stop %",
            min_value=0.1,
            value=float(st.session_state.trailing_stop_percent),
            step=0.1,
            key="trailing_stop_percent_input"
        )

        st.session_state.use_tp1 = st.toggle(
            "TP1 Teilgewinn aktiv",
            value=st.session_state.use_tp1,
    )

    st.subheader("Portfolio Risiko")

    positions = st.session_state.paper_positions

    if positions:
        total_risk_eur = 0.0
        risk_rows = []

        for pos in positions:
            entry = float(pos["entry"])
            stop_loss = float(pos["stop_loss"])
            qty = float(pos["qty"])

            risk_per_share = entry - stop_loss
            position_risk = risk_per_share * qty

            total_risk_eur += position_risk

            risk_rows.append({
                "symbol": pos["symbol"],
                "entry": round(entry, 2),
                "stop_loss": round(stop_loss, 2),
                "qty": round(qty, 2),
                "risk_eur": round(position_risk, 2),
            })

        r1, r2 = st.columns(2)

        st.session_state.max_portfolio_risk_eur = st.number_input(
            "Max Portfolio Risiko (€)",
            min_value=1.0,
            value=float(st.session_state.max_portfolio_risk_eur),
            step=50.0,
        )

        with r1:
            st.metric("Gesamtrisiko (€)", f"{total_risk_eur:.2f}")

        with r2:
            st.metric("Offene Risiko-Trades", len(positions))

        st.dataframe(risk_rows, width="stretch")

        if total_risk_eur > st.session_state.max_portfolio_risk_eur:
            st.error("Portfolio Risiko überschreitet dein gesetztes Limit.")
        else:
            st.success("Portfolio Risiko liegt innerhalb deines Limits.")
    else:
        st.info("Aktuell kein offenes Risiko im Portfolio.")

    st.subheader("Positionen kompakt")

    positions = st.session_state.paper_positions

    if positions:
        compact_rows = []

        for pos in positions:
            data = load_data(pos["symbol"], "5d", "1d")

            if not data.empty:
                current_price = float(data["Close"].iloc[-1])
            else:
                current_price = float(pos["entry"])

            pnl_abs = (current_price - float(pos["entry"])) * float(pos["qty"])
            pnl_pct = ((current_price - float(pos["entry"])) / float(pos["entry"]) * 100) if float(pos["entry"]) != 0 else 0.0

            compact_rows.append({
                "symbol": pos["symbol"],
                "entry": round(float(pos["entry"]), 2),
                "current": round(current_price, 2),
                "qty": round(float(pos["qty"]), 2),
                "pnl": round(pnl_abs, 2),
                "pnl_pct": round(pnl_pct, 2),
                "sl": round(float(pos["stop_loss"]), 2),
                "tp": round(float(pos["take_profit"]), 2),
            })

        st.dataframe(compact_rows, width="stretch")
    else:
        st.caption("Keine offenen Positionen.")

    # =====================================================
    # TRADE IDEE ÜBERNEHMEN
    # =====================================================
    st.subheader("Trade Idee")

    if trade:
        t1, t2, t3, t4, t5 = st.columns(5)

        t1.metric("Symbol", str(trade["symbol"]))
        t2.metric("Entry", f'{float(trade["entry"]):.2f}')
        t3.metric("Stop Loss", f'{float(trade["stop_loss"]):.2f}')
        t4.metric("TP1", f'{float(trade["take_profit_1"]):.2f}')
        t5.metric("TP2", f'{float(trade["take_profit_2"]):.2f}')
        t5.metric("RR", f'{float(trade["rr"]):.2f}')

        default_qty = 1.0

        if trade and "suggested_qty" in trade:
            default_qty = max(1.0, round(float(trade["suggested_qty"])))

        qty = st.number_input(
            "Stückzahl",
            min_value=1.0,
            value=float(default_qty),
            step=1.0
        )

        st.caption("Du kannst die Stückzahl manuell anpassen")

        entry = float(trade["entry"])
        stop_loss = float(trade["stop_loss"])

        risk_per_share = entry - stop_loss
        total_risk = risk_per_share * qty

        st.metric("Aktuelles Risiko (€)", f"{total_risk:.2f}")

        # =====================
        # MAXIMAL MÖGLICHE STÜCKZAHL AUS RISIKO-LIMIT
        # =====================

        current_portfolio_risk = 0.0
        for pos in st.session_state.paper_positions:
            pos_entry = float(pos["entry"])
            pos_stop = float(pos["stop_loss"])
            pos_qty = float(pos["qty"])

            pos_risk_per_share = pos_entry - pos_stop
            current_portfolio_risk += pos_risk_per_share * pos_qty

        remaining_risk_capacity = float(st.session_state.max_portfolio_risk_eur) - current_portfolio_risk

        if risk_per_share > 0:
            max_qty_by_risk = max(0.0, remaining_risk_capacity / risk_per_share)
        else:
            max_qty_by_risk = 0.0

        st.caption(f"Freies Risiko im Portfolio: {remaining_risk_capacity:.2f} €")
        st.caption(f"Maximal mögliche Stückzahl nach Risiko-Limit: {max_qty_by_risk:.2f}")

        if st.button("Max nach Risiko setzen", width="stretch"):
            if max_qty_by_risk >= 1:
                qty = float(round(max_qty_by_risk))
                st.session_state.paper_trade_idea["suggested_qty"] = qty
                st.rerun()
            else:
                st.warning("Für dieses Risiko-Limit ist aktuell keine Stückzahl möglich.")

        if qty > max_qty_by_risk and max_qty_by_risk >= 0:
            st.warning("Die gewählte Stückzahl ist höher als dein aktuelles Risiko-Limit erlaubt.")

        if trade and "risk_amount_eur" in trade:
            st.caption(f"Basierend auf Risiko: {trade['risk_amount_eur']:.2f} €")

        if st.button("Position eröffnen", width="stretch"):
            entry_value = float(trade["entry"]) * float(qty)

            if entry_value > st.session_state.paper_cash:
                st.error("Nicht genug Paper Cash für diese Position.")
            else:
                # =====================
                # RISIKO NEUER TRADE
                # =====================
                new_trade_risk = (float(trade["entry"]) - float(trade["stop_loss"])) * float(qty)

                current_portfolio_risk = 0.0
                for pos in st.session_state.paper_positions:
                    entry = float(pos["entry"])
                    stop_loss = float(pos["stop_loss"])
                    pos_qty = float(pos["qty"])

                    risk_per_share = entry - stop_loss
                    current_portfolio_risk += risk_per_share * pos_qty

                future_total_risk = current_portfolio_risk + new_trade_risk

                if future_total_risk > float(st.session_state.max_portfolio_risk_eur):
                    st.error("Diese Position würde dein Portfolio-Risiko-Limit überschreiten.")
                else:
                    new_position = {
                        "id": len(st.session_state.paper_trade_history) + len(st.session_state.paper_positions) + 1,
                        "symbol": str(trade["symbol"]),
                        "entry": float(trade["entry"]),
                        "stop_loss": float(trade["stop_loss"]),
                        "take_profit_1": float(trade["take_profit_1"]),
                        "take_profit_2": float(trade["take_profit_2"]),
                        "tp1_hit": False,
                        "rr": float(trade["rr"]),
                        "qty": float(qty),
                        "highest_price": float(trade["entry"]),
                    }

                    st.session_state.paper_cash -= entry_value
                    st.session_state.paper_positions.append(new_position)

                    st.session_state.paper_trade_history.append({
                        "type": "OPEN",
                        "symbol": str(trade["symbol"]),
                        "entry": float(trade["entry"]),
                        "qty": float(qty),
                    })

                    st.success("Position eröffnet.")
                    st.rerun()
    else:
        st.info("Noch keine Trade Idee aus der Analyse übernommen.")

    st.divider()

    st.session_state.trailing_stop_percent = st.number_input(
        "Trailing Stop %",
        min_value=0.1,
        value=float(st.session_state.trailing_stop_percent),
        step=0.1,
    )

    # =====================================================
    # OFFENE POSITIONEN
    # =====================================================
    st.subheader("Offene Positionen")

    if positions:
        positions_to_remove = []

        for idx, position in enumerate(positions):
            data = load_data(position["symbol"], "5d", "1d")

            if not data.empty:
                current_price = float(data["Close"].iloc[-1])
            else:
                current_price = float(position["entry"])

            pnl_abs = (current_price - float(position["entry"])) * float(position["qty"])
            pnl_pct = ((current_price - float(position["entry"])) / float(position["entry"]) * 100) if float(position["entry"]) != 0 else 0.0

            stored_high = float(position.get("highest_price", position["entry"]))

            if st.session_state.use_tp1 and (not position.get("tp1_hit", False)) and current_price >= float(position["take_profit_1"]):
                half_qty = max(1.0, float(position["qty"]) / 2)

                # falls qty = 1, dann nicht gleich komplett zerlegen
                if half_qty >= float(position["qty"]):
                    half_qty = max(1.0, float(position["qty"]) - 1)

                if half_qty > 0:
                    close_value = current_price * half_qty
                    st.session_state.paper_cash += close_value

                    realized_pnl_abs = (current_price - float(position["entry"])) * half_qty
                    realized_pnl_pct = ((current_price - float(position["entry"])) / float(position["entry"]) * 100) if float(position["entry"]) != 0 else 0.0

                    st.session_state.paper_trade_history.append({
                        "type": "TP1",
                        "symbol": str(position["symbol"]),
                        "exit": current_price,
                        "qty": half_qty,
                        "pnl_abs": realized_pnl_abs,
                        "pnl_pct": realized_pnl_pct,
                    })

                    st.session_state.trade_journal.append({
                        "symbol": str(position["symbol"]),
                        "entry": float(position["entry"]),
                        "exit": current_price,
                        "pnl": realized_pnl_abs,
                        "pnl_pct": realized_pnl_pct,
                        "type": "TP1",
                    })

                    remaining_qty = float(position["qty"]) - half_qty

                    st.session_state.paper_positions[idx]["qty"] = remaining_qty
                    st.session_state.paper_positions[idx]["tp1_hit"] = True
                    st.session_state.paper_positions[idx]["stop_loss"] = float(position["entry"])

                    st.success(f"TP1 erreicht: {position['symbol']} | Teilgewinn gesichert")
                    st.rerun()

            if current_price > stored_high:
                st.session_state.paper_positions[idx]["highest_price"] = current_price
                stored_high = current_price

            if st.session_state.use_trailing_stop:
                trailing_stop_price = stored_high * (1 - float(st.session_state.trailing_stop_percent) / 100)
                current_stop = float(position["stop_loss"])
                new_stop = max(current_stop, trailing_stop_price)

                st.session_state.paper_positions[idx]["stop_loss"] = new_stop
                position = st.session_state.paper_positions[idx]

            with st.container(border=True):
                p1, p2, p3, p4 = st.columns(4)
                p1.metric("Symbol", str(position["symbol"]))
                p2.metric("Aktuell", f"{current_price:.2f}")
                p3.metric("PnL", f"{pnl_abs:.2f}")
                p4.metric("PnL %", f"{pnl_pct:.2f}%")

                st.write(f"**Entry:** {float(position['entry']):.2f}")
                st.write(f"**Stop Loss:** {float(position['stop_loss']):.2f}")
                st.write(f"**TP1:** {float(position['take_profit_1']):.2f}")
                st.write(f"**TP2:** {float(position['take_profit_2']):.2f}")
                st.write(f"**Stückzahl:** {float(position['qty']):.2f}")
                st.write(f"**Highest Price:** {float(position.get('highest_price', position['entry'])):.2f}")
                st.write(f"**Trailing Stop:** {float(position['stop_loss']):.2f}")

                # =========================================
                # AUTO CLOSE: SL / TP
                # =========================================
                if current_price <= float(position["stop_loss"]):
                    close_value = current_price * float(position["qty"])
                    st.session_state.paper_cash += close_value

                    st.session_state.paper_trade_history.append({
                        "type": "SL",
                        "symbol": str(position["symbol"]),
                        "exit": current_price,
                        "qty": float(position["qty"]),
                        "pnl_abs": pnl_abs,
                        "pnl_pct": pnl_pct,
                    })

                    st.session_state.trade_journal.append({
                        "symbol": str(position["symbol"]),
                        "entry": float(position["entry"]),
                        "exit": current_price,
                        "pnl": pnl_abs,
                        "pnl_pct": pnl_pct,
                        "type": "SL",
                    })

                    positions_to_remove.append(idx)
                    st.warning(f"Stop Loss ausgelöst: {position['symbol']}")
                    continue

                if current_price >= float(position["take_profit_2"]):
                    close_value = current_price * float(position["qty"])
                    st.session_state.paper_cash += close_value

                    st.session_state.paper_trade_history.append({
                        "type": "TP",
                        "symbol": str(position["symbol"]),
                        "exit": current_price,
                        "qty": float(position["qty"]),
                        "pnl_abs": pnl_abs,
                        "pnl_pct": pnl_pct,
                    })

                    st.session_state.trade_journal.append({
                        "symbol": str(position["symbol"]),
                        "entry": float(position["entry"]),
                        "exit": current_price,
                        "pnl": pnl_abs,
                        "pnl_pct": pnl_pct,
                        "type": "TP",
                    })

                    positions_to_remove.append(idx)
                    st.success(f"Take Profit erreicht: {position['symbol']}")
                    continue

                partial_qty = st.number_input(
                    f"Teilverkauf Stückzahl - {position['symbol']} #{idx}",
                    min_value=1.0,
                    max_value=float(position["qty"]),
                    value=1.0,
                    step=1.0,
                    key=f"partial_qty_{idx}"
                )

                if st.button(f"Teilverkauf - {position['symbol']} #{idx}", key=f"partial_close_{idx}", width="stretch"):
                    sell_qty = float(partial_qty)
                    close_value = current_price * sell_qty

                    st.session_state.paper_cash += close_value

                    realized_pnl_abs = (current_price - float(position["entry"])) * sell_qty
                    realized_pnl_pct = ((current_price - float(position["entry"])) / float(position["entry"]) * 100) if float(position["entry"]) != 0 else 0.0

                    st.session_state.paper_trade_history.append({
                        "type": "PARTIAL_CLOSE",
                        "symbol": str(position["symbol"]),
                        "exit": current_price,
                        "qty": sell_qty,
                        "pnl_abs": realized_pnl_abs,
                        "pnl_pct": realized_pnl_pct,
                    })

                    st.session_state.trade_journal.append({
                        "symbol": str(position["symbol"]),
                        "entry": float(position["entry"]),
                        "exit": current_price,
                        "pnl": realized_pnl_abs,
                        "pnl_pct": realized_pnl_pct,
                        "type": "PARTIAL",
                    })

                    remaining_qty = float(position["qty"]) - sell_qty

                    if remaining_qty <= 0:
                        positions_to_remove.append(idx)
                    else:
                        # Menge reduzieren
                        st.session_state.paper_positions[idx]["qty"] = remaining_qty

                        # =====================
                        # BREAK EVEN
                        # =====================
                        if st.session_state.use_break_even:
                            st.session_state.paper_positions[idx]["stop_loss"] = float(position["entry"])
                            st.info("Stop Loss auf Break-Even gesetzt")

                if st.button(f"Position schließen - {position['symbol']} #{idx}", key=f"close_{idx}", width="stretch"):
                    close_value = current_price * float(position["qty"])
                    st.session_state.paper_cash += close_value

                    st.session_state.paper_trade_history.append({
                        "type": "CLOSE",
                        "symbol": str(position["symbol"]),
                        "exit": current_price,
                        "qty": float(position["qty"]),
                        "pnl_abs": pnl_abs,
                        "pnl_pct": pnl_pct,
                    })

                    st.session_state.trade_journal.append({
                        "symbol": str(position["symbol"]),
                        "entry": float(position["entry"]),
                        "exit": current_price,
                        "pnl": pnl_abs,
                        "pnl_pct": pnl_pct,
                        "type": "MANUAL",
                    })

                    positions_to_remove.append(idx)
                    st.success(f"Position geschlossen: {position['symbol']}")

        if positions_to_remove:
            st.session_state.paper_positions = [
                pos for i, pos in enumerate(st.session_state.paper_positions)
                if i not in positions_to_remove
            ]
            st.rerun()
    else:
        st.info("Aktuell keine offenen Positionen.")

    st.divider()

    # =====================================================
    # EQUITY VERLAUF
    # =====================================================
    st.subheader("Equity Verlauf")

    if st.session_state.equity_curve:
        st.line_chart(st.session_state.equity_curve, width="stretch")

    st.caption(f"Peak Equity: {peak_equity:.2f}")
    st.caption(f"Aktueller Drawdown: {drawdown_pct:.2f}%")
    st.caption(f"Gesamtperformance: {performance_pct:.2f}%")

    st.divider()

    # =====================================================
    # HISTORIE
    # =====================================================
    st.subheader("Historie")

    history = st.session_state.paper_trade_history
    if history:
        st.dataframe(history, width="stretch")
    else:
        st.caption("Noch keine Trades in der Historie.")