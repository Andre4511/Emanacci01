import streamlit as st
from utils import load_data


def _init_paper_state() -> None:
    defaults = {
        "paper_trade_idea": None,
        "paper_positions": [],
        "paper_cash": 10000.0,
        "paper_trade_history": [],
        "trade_journal": [],
        "equity_curve": [],
        "paper_peak_equity": 0.0,
        "max_portfolio_risk_eur": 500.0,
        "use_break_even": True,
        "use_trailing_stop": True,
        "use_tp1": True,
        "trailing_stop_percent": 2.0,
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def _get_current_price(symbol: str, fallback: float) -> float:
    data = load_data(symbol, "5d", "1d")
    if not data.empty:
        return float(data["Close"].iloc[-1])
    return float(fallback)


def _position_risk_eur(position: dict) -> float:
    entry = float(position["entry"])
    stop_loss = float(position["stop_loss"])
    qty = float(position["qty"])
    return max(0.0, (entry - stop_loss) * qty)


def _append_journal_entry(
    position: dict,
    exit_price: float,
    pnl_abs: float,
    pnl_pct: float,
    trade_type: str,
) -> None:
    st.session_state.trade_journal.append({
        "symbol": str(position["symbol"]),
        "entry": float(position["entry"]),
        "exit": float(exit_price),
        "pnl": float(pnl_abs),
        "pnl_pct": float(pnl_pct),
        "type": str(trade_type),
        "signal": position.get("signal", "-"),
        "risk": position.get("risk", "-"),
        "trend": position.get("trend", "-"),
        "strength": position.get("strength", "-"),
        "main_mistake": position.get("main_mistake", "-"),
        "main_mistake_type": position.get("main_mistake_type", "-"),
        "learning_step": position.get("learning_step", ""),
    })


def _render_trade_idea_preview(trade: dict | None) -> None:
    if not trade:
        return

    with st.expander("Analyse-Vorschau", expanded=False):
        st.write(f"**Signal:** {trade.get('signal', '-')}")
        st.write(f"**Risiko:** {trade.get('risk', '-')}")
        st.write(f"**Trend:** {trade.get('trend', '-')}")
        st.write(f"**Stärke:** {trade.get('strength', '-')}")
        st.write(f"**Diagnose:** {trade.get('diagnosis_summary', '-')}")
        if trade.get("main_mistake"):
            st.write(f"**Hauptfehler:** {trade.get('main_mistake')}")
        if trade.get("main_mistake_type"):
            st.caption(f"Typ: {trade.get('main_mistake_type')}")
        if trade.get("learning_step"):
            st.write(f"**Nächster Lernschritt:** {trade.get('learning_step')}")


def render_paper_trading_page() -> None:
    _init_paper_state()

    st.title("Paper Trading")

    trade = st.session_state.paper_trade_idea
    positions = st.session_state.paper_positions
    start_capital = 10000.0

    # =====================================================
    # ADVANCED
    # =====================================================
    with st.expander("Advanced Einstellungen", expanded=False):
        st.session_state.use_break_even = st.toggle(
            "Break-Even nach Teilverkauf",
            value=st.session_state.use_break_even,
            key="paper_use_break_even",
        )

        st.session_state.use_trailing_stop = st.toggle(
            "Trailing Stop aktiv",
            value=st.session_state.use_trailing_stop,
            key="paper_use_trailing_stop",
        )

        st.session_state.trailing_stop_percent = st.number_input(
            "Trailing Stop %",
            min_value=0.1,
            value=float(st.session_state.trailing_stop_percent),
            step=0.1,
            key="paper_trailing_stop_percent",
        )

        st.session_state.use_tp1 = st.toggle(
            "TP1 Teilgewinn aktiv",
            value=st.session_state.use_tp1,
            key="paper_use_tp1",
        )

        st.session_state.max_portfolio_risk_eur = st.number_input(
            "Max Portfolio Risiko (€)",
            min_value=1.0,
            value=float(st.session_state.max_portfolio_risk_eur),
            step=50.0,
            key="paper_max_portfolio_risk",
        )

    if st.session_state.get("advanced_mode", False):
        _render_trade_idea_preview(trade)

    # =====================================================
    # EQUITY / PERFORMANCE
    # =====================================================
    total_open_value = 0.0
    total_open_pnl = 0.0

    for pos in positions:
        current_price = _get_current_price(pos["symbol"], pos["entry"])
        total_open_value += current_price * float(pos["qty"])
        total_open_pnl += (current_price - float(pos["entry"])) * float(pos["qty"])

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

    k1, k2 = st.columns(2)
    k1.metric("Cash", f"{st.session_state.paper_cash:.2f}")
    k2.metric("Equity", f"{equity:.2f}")

    k3, k4 = st.columns(2)
    k3.metric("Performance", f"{performance_pct:.2f}%")
    k4.metric("Drawdown", f"{drawdown_pct:.2f}%")

    st.divider()

    # =====================================================
    # PORTFOLIO ÜBERBLICK
    # =====================================================
    st.subheader("Portfolio Überblick")

    if positions:
        pnl_values = []

        for pos in positions:
            current_price = _get_current_price(pos["symbol"], pos["entry"])
            pnl_abs = (current_price - float(pos["entry"])) * float(pos["qty"])
            pnl_values.append({"symbol": pos["symbol"], "pnl": pnl_abs})

        best_trade = max(pnl_values, key=lambda x: x["pnl"])
        worst_trade = min(pnl_values, key=lambda x: x["pnl"])

        p1, p2, p3 = st.columns(3)
        p1.metric("Offene Positionen", len(positions))
        p2.metric("Bester Trade", f"{best_trade['symbol']} ({best_trade['pnl']:.2f})")
        p3.metric("Schwächster Trade", f"{worst_trade['symbol']} ({worst_trade['pnl']:.2f})")
    else:
        st.info("Noch kein Portfolio aufgebaut.")

    st.divider()

    # =====================================================
    # PORTFOLIO RISIKO
    # =====================================================
    st.subheader("Portfolio Risiko")

    if positions:
        total_risk_eur = 0.0
        risk_rows = []

        for pos in positions:
            position_risk = _position_risk_eur(pos)
            total_risk_eur += position_risk

            risk_rows.append({
                "symbol": pos["symbol"],
                "entry": round(float(pos["entry"]), 2),
                "stop_loss": round(float(pos["stop_loss"]), 2),
                "qty": round(float(pos["qty"]), 2),
                "risk_eur": round(position_risk, 2),
            })

        r1, r2 = st.columns(2)
        r1.metric("Gesamtrisiko (€)", f"{total_risk_eur:.2f}")
        r2.metric("Offene Risiko-Trades", len(positions))

        if total_risk_eur > st.session_state.max_portfolio_risk_eur:
            st.error("Portfolio Risiko überschreitet dein gesetztes Limit.")
        else:
            st.success("Portfolio Risiko liegt innerhalb deines Limits.")

        st.dataframe(risk_rows, width="stretch")
    else:
        st.info("Aktuell kein offenes Risiko im Portfolio.")

    st.divider()

    # =====================================================
    # TRADE IDEE
    # =====================================================
    st.subheader("Trade Idee")

    if trade:
        t1, t2 = st.columns(2)
        t1.metric("Symbol", str(trade["symbol"]))
        t2.metric("Entry", f'{float(trade["entry"]):.2f}')

        t3, t4, t5 = st.columns(3)
        t3.metric("Stop Loss", f'{float(trade["stop_loss"]):.2f}')
        t4.metric("TP1", f'{float(trade["take_profit_1"]):.2f}')
        t5.metric("TP2", f'{float(trade["take_profit_2"]):.2f}')

        default_qty = 1.0
        if "suggested_qty" in trade:
            default_qty = max(1.0, round(float(trade["suggested_qty"])))

        qty = st.number_input(
            "Stückzahl",
            min_value=1.0,
            value=float(default_qty),
            step=1.0,
            key="paper_qty_input",
        )

        if "risk_amount_eur" in trade:
            st.caption(f"Basierend auf Risiko: {trade['risk_amount_eur']:.2f} €")

        entry_value = float(trade["entry"]) * float(qty)
        risk_per_share = float(trade["entry"]) - float(trade["stop_loss"])
        total_risk = risk_per_share * float(qty)

        st.metric("Aktuelles Risiko (€)", f"{total_risk:.2f}")

        current_portfolio_risk = 0.0
        for pos in positions:
            current_portfolio_risk += _position_risk_eur(pos)

        remaining_risk_capacity = float(st.session_state.max_portfolio_risk_eur) - current_portfolio_risk
        max_qty_by_risk = max(0.0, remaining_risk_capacity / risk_per_share) if risk_per_share > 0 else 0.0

        st.caption(f"Freies Risiko im Portfolio: {remaining_risk_capacity:.2f} €")
        st.caption(f"Maximal mögliche Stückzahl nach Risiko-Limit: {max_qty_by_risk:.2f}")

        if qty > max_qty_by_risk and max_qty_by_risk >= 0:
            st.warning("Die gewählte Stückzahl ist höher als dein aktuelles Risiko-Limit erlaubt.")

        if st.button("Max nach Risiko setzen", use_container_width=True, key="paper_set_max_risk_qty"):
            if max_qty_by_risk >= 1:
                st.session_state.paper_trade_idea["suggested_qty"] = float(round(max_qty_by_risk))
                st.rerun()
            else:
                st.warning("Für dieses Risiko-Limit ist aktuell keine Stückzahl möglich.")

        if st.button("Position eröffnen", use_container_width=True, key="paper_open_position"):
            if entry_value > st.session_state.paper_cash:
                st.error("Nicht genug Paper Cash für diese Position.")
            else:
                new_trade_risk = risk_per_share * float(qty)
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
                        "qty": float(qty),
                        "tp1_hit": False,
                        "highest_price": float(trade["entry"]),
                        "signal": trade.get("signal", "-"),
                        "risk": trade.get("risk", "-"),
                        "trend": trade.get("trend", "-"),
                        "strength": trade.get("strength", "-"),
                        "main_mistake": trade.get("main_mistake", "-"),
                        "main_mistake_type": trade.get("main_mistake_type", "-"),
                        "mistakes": trade.get("mistakes", []),
                        "learning_step": trade.get("learning_step", ""),
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

    # =====================================================
    # POSITIONEN KOMPAKT
    # =====================================================
    st.subheader("Positionen kompakt")

    if positions:
        compact_rows = []

        for pos in positions:
            current_price = _get_current_price(pos["symbol"], pos["entry"])
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
                "tp1": round(float(pos["take_profit_1"]), 2),
                "tp2": round(float(pos["take_profit_2"]), 2),
            })

        st.dataframe(compact_rows, width="stretch")
    else:
        st.caption("Keine offenen Positionen.")

    st.divider()

    # =====================================================
    # OFFENE POSITIONEN
    # =====================================================
    st.subheader("Offene Positionen")

    if positions:
        positions_to_remove = []

        for idx, position in enumerate(positions):
            current_price = _get_current_price(position["symbol"], position["entry"])

            stored_high = float(position.get("highest_price", position["entry"]))
            if current_price > stored_high:
                st.session_state.paper_positions[idx]["highest_price"] = current_price
                stored_high = current_price

            if st.session_state.use_trailing_stop:
                trailing_stop_price = stored_high * (
                    1 - float(st.session_state.trailing_stop_percent) / 100
                )
                current_stop = float(position["stop_loss"])
                new_stop = max(current_stop, trailing_stop_price)
                st.session_state.paper_positions[idx]["stop_loss"] = new_stop
                position = st.session_state.paper_positions[idx]

            pnl_abs = (current_price - float(position["entry"])) * float(position["qty"])
            pnl_pct = ((current_price - float(position["entry"])) / float(position["entry"]) * 100) if float(position["entry"]) != 0 else 0.0

            with st.container(border=True):
                p1, p2 = st.columns(2)
                p1.metric("Symbol", str(position["symbol"]))
                p2.metric("Aktuell", f"{current_price:.2f}")

                p3, p4 = st.columns(2)
                p3.metric("PnL", f"{pnl_abs:.2f}")
                p4.metric("PnL %", f"{pnl_pct:.2f}%")

                st.write(f"**Entry:** {float(position['entry']):.2f}")
                st.write(f"**Stop Loss:** {float(position['stop_loss']):.2f}")
                st.write(f"**TP1:** {float(position['take_profit_1']):.2f}")
                st.write(f"**TP2:** {float(position['take_profit_2']):.2f}")
                st.write(f"**Stückzahl:** {float(position['qty']):.2f}")
                st.write(f"**Highest Price:** {float(position.get('highest_price', position['entry'])):.2f}")

                if position.get("main_mistake") not in [None, "", "-"]:
                    st.caption(f"Hauptfehler aus Analyse: {position.get('main_mistake')}")

                # TP1
                if (
                    st.session_state.use_tp1
                    and not position.get("tp1_hit", False)
                    and current_price >= float(position["take_profit_1"])
                ):
                    half_qty = max(1.0, float(position["qty"]) / 2)

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

                        _append_journal_entry(
                            position=position,
                            exit_price=current_price,
                            pnl_abs=realized_pnl_abs,
                            pnl_pct=realized_pnl_pct,
                            trade_type="TP1",
                        )

                        remaining_qty = float(position["qty"]) - half_qty
                        st.session_state.paper_positions[idx]["qty"] = remaining_qty
                        st.session_state.paper_positions[idx]["tp1_hit"] = True

                        if st.session_state.use_break_even:
                            st.session_state.paper_positions[idx]["stop_loss"] = float(position["entry"])
                            st.info("Stop Loss auf Break-Even gesetzt")

                        st.success(f"TP1 erreicht: {position['symbol']}")
                        st.rerun()

                # SL
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

                    _append_journal_entry(
                        position=position,
                        exit_price=current_price,
                        pnl_abs=pnl_abs,
                        pnl_pct=pnl_pct,
                        trade_type="SL",
                    )

                    positions_to_remove.append(idx)
                    st.warning(f"Stop Loss ausgelöst: {position['symbol']}")
                    continue

                # TP2
                if current_price >= float(position["take_profit_2"]):
                    close_value = current_price * float(position["qty"])
                    st.session_state.paper_cash += close_value

                    st.session_state.paper_trade_history.append({
                        "type": "TP2",
                        "symbol": str(position["symbol"]),
                        "exit": current_price,
                        "qty": float(position["qty"]),
                        "pnl_abs": pnl_abs,
                        "pnl_pct": pnl_pct,
                    })

                    _append_journal_entry(
                        position=position,
                        exit_price=current_price,
                        pnl_abs=pnl_abs,
                        pnl_pct=pnl_pct,
                        trade_type="TP2",
                    )

                    positions_to_remove.append(idx)
                    st.success(f"TP2 erreicht: {position['symbol']}")
                    continue

                partial_qty = st.number_input(
                    f"Teilverkauf Stückzahl - {position['symbol']} #{idx}",
                    min_value=1.0,
                    max_value=float(position["qty"]),
                    value=1.0,
                    step=1.0,
                    key=f"partial_qty_{idx}",
                )

                if st.button(f"Teilverkauf - {position['symbol']} #{idx}", key=f"partial_close_{idx}", use_container_width=True):
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

                    _append_journal_entry(
                        position=position,
                        exit_price=current_price,
                        pnl_abs=realized_pnl_abs,
                        pnl_pct=realized_pnl_pct,
                        trade_type="PARTIAL",
                    )

                    remaining_qty = float(position["qty"]) - sell_qty

                    if remaining_qty <= 0:
                        positions_to_remove.append(idx)
                    else:
                        st.session_state.paper_positions[idx]["qty"] = remaining_qty

                        if st.session_state.use_break_even:
                            st.session_state.paper_positions[idx]["stop_loss"] = float(position["entry"])
                            st.info("Stop Loss auf Break-Even gesetzt")

                    st.success(f"Teilverkauf ausgeführt: {sell_qty:.0f} Stück von {position['symbol']}")
                    st.rerun()

                if st.button(f"Position schließen - {position['symbol']} #{idx}", key=f"close_{idx}", use_container_width=True):
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

                    _append_journal_entry(
                        position=position,
                        exit_price=current_price,
                        pnl_abs=pnl_abs,
                        pnl_pct=pnl_pct,
                        trade_type="MANUAL",
                    )

                    positions_to_remove.append(idx)
                    st.success(f"Position geschlossen: {position['symbol']}")
                    st.rerun()

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