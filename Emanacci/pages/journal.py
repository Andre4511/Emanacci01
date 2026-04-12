import pandas as pd
import streamlit as st


def _calculate_progress(df: pd.DataFrame):
    if df.empty or "main_mistake_type" not in df.columns:
        return None

    recent = df.tail(10).copy()
    older = df.iloc[:-10].copy() if len(df) > 10 else pd.DataFrame()

    if recent.empty:
        return None

    results = []

    for mistake_type in ["Timing-Fehler", "Trend-Fehler", "Risiko-Fehler"]:
        recent_count = int((recent["main_mistake_type"].astype(str) == mistake_type).sum())

        if older.empty:
            trend = "gleich"
        else:
            older_count = int((older["main_mistake_type"].astype(str) == mistake_type).sum())
            recent_ratio = recent_count / max(len(recent), 1)
            older_ratio = older_count / max(len(older), 1)

            if recent_ratio < older_ratio:
                trend = "besser"
            elif recent_ratio > older_ratio:
                trend = "schlechter"
            else:
                trend = "gleich"

        results.append((mistake_type, trend))

    winrate_trend = "gleich"
    if "pnl" in df.columns and not older.empty:
        recent_winrate = float((recent["pnl"] > 0).mean())
        older_winrate = float((older["pnl"] > 0).mean())

        if recent_winrate > older_winrate:
            winrate_trend = "besser"
        elif recent_winrate < older_winrate:
            winrate_trend = "schlechter"

    return results, winrate_trend


def _build_trader_profile(df: pd.DataFrame):
    if df.empty or "main_mistake_type" not in df.columns:
        return None

    valid = df["main_mistake_type"].copy()

    valid = valid.astype(str).str.strip()
    valid = valid[~valid.isin(["", "-", "nan", "None", "none"])]

    if valid.empty:
        return {
            "title": "Noch kein klares Profil",
            "dominant_type": "",
        }

    counts = valid.value_counts()

    if counts.empty:
        return {
            "title": "Noch kein klares Profil",
            "dominant_type": "",
        }

    dominant_type = counts.idxmax()

    if dominant_type == "Timing-Fehler":
        title = "Du entscheidest oft etwas zu früh."
    elif dominant_type == "Trend-Fehler":
        title = "Du ignorierst noch zu oft die Haupttrend-Richtung."
    elif dominant_type == "Risiko-Fehler":
        title = "Dein Risiko-Management ist aktuell dein wichtigstes Lernfeld."
    else:
        title = "Du entwickelst gerade dein eigenes Trading-Profil."

    return {
        "title": title,
        "dominant_type": dominant_type,
    }


def _build_combined_insight(profile, progress):
    if not profile:
        return None

    text = profile["title"]

    if progress:
        results, winrate_trend = progress
        dominant = profile.get("dominant_type", "")

        for m_type, trend in results:
            if m_type == dominant:
                if trend == "besser":
                    text += " In diesem Bereich wirst du bereits besser."
                elif trend == "schlechter":
                    text += " In diesem Bereich verschlechterst du dich aktuell etwas."
                break

        if winrate_trend == "besser":
            text += " Deine Trefferquote verbessert sich."
        elif winrate_trend == "schlechter":
            text += " Deine Trefferquote ist zuletzt schwächer geworden."

    return text


def _build_next_learning_goal(df: pd.DataFrame, progress):
    if df.empty or "main_mistake_type" not in df.columns:
        return None

    valid = df["main_mistake_type"].copy()

    valid = valid.astype(str).str.strip()
    valid = valid[~valid.isin(["", "-", "nan", "None", "none"])]

    if valid.empty:
        return "Sammle weitere Trades, um ein klares Lernziel ableiten zu können."

    counts = valid.value_counts()

    if counts.empty:
        return "Sammle weitere Trades, um ein klares Lernziel ableiten zu können."

    most_common = counts.idxmax()

    if most_common == "Timing-Fehler":
        goal = "Konzentriere dich darauf, erst nach klarer Bestätigung einzusteigen."
    elif most_common == "Trend-Fehler":
        goal = "Achte stärker darauf, nur in Richtung des Haupttrends zu handeln."
    elif most_common == "Risiko-Fehler":
        goal = "Plane Stop-Loss, Ziel und Positionsgröße bewusster."
    else:
        goal = "Achte auf saubere Einstiege und besseres Risiko-Management."

    if progress:
        results, _ = progress
        for m_type, trend in results:
            if m_type == most_common:
                if trend == "besser":
                    goal += " Du wirst hier bereits besser."
                elif trend == "schlechter":
                    goal += " Hier brauchst du aktuell wieder mehr Aufmerksamkeit."
                break

    return goal


def _build_level_system(df: pd.DataFrame):
    if df.empty:
        return {
            "level": "Anfänger",
            "score": 0,
            "next_level": "Lernender",
            "hint": "Starte mit ersten Trades und sammle Erfahrungen.",
            "trade_count": 0,
            "winrate": 0.0,
            "mistake_ratio": 1.0,
        }

    trade_count = len(df)
    wins = int((df["pnl"] > 0).sum()) if "pnl" in df.columns else 0
    winrate = (wins / trade_count * 100) if trade_count > 0 else 0.0

    if "main_mistake_type" in df.columns:
        mistake_df = df[df["main_mistake_type"].astype(str).str.strip().ne("-")].copy()
    else:
        mistake_df = pd.DataFrame()

    mistake_count = len(mistake_df)
    mistake_ratio = (mistake_count / trade_count) if trade_count > 0 else 1.0

    score = 0

    if trade_count >= 5:
        score += 1
    if trade_count >= 15:
        score += 1
    if trade_count >= 30:
        score += 1

    if winrate >= 45:
        score += 1
    if winrate >= 55:
        score += 1

    if mistake_ratio <= 0.8:
        score += 1
    if mistake_ratio <= 0.5:
        score += 1

    if score <= 2:
        level = "Anfänger"
        next_level = "Lernender"
        hint = "Konzentriere dich zuerst auf saubere Einstiege und weniger typische Fehler."
    elif score <= 4:
        level = "Lernender"
        next_level = "Solider Trader"
        hint = "Du baust gerade Grundlagen auf. Arbeite weiter an Timing und Risiko."
    elif score <= 6:
        level = "Solider Trader"
        next_level = "Fortgeschritten"
        hint = "Deine Trades werden stabiler. Jetzt geht es um Konstanz und Disziplin."
    else:
        level = "Fortgeschritten"
        next_level = "Stabilität halten"
        hint = "Du hast bereits gute Muster aufgebaut. Halte deine Qualität konstant."

    return {
        "level": level,
        "score": score,
        "next_level": next_level,
        "hint": hint,
        "trade_count": trade_count,
        "winrate": winrate,
        "mistake_ratio": mistake_ratio,
    }


def render_journal_page() -> None:
    st.title("Journal")

    journal = st.session_state.get("trade_journal", [])

    if not journal:
        st.info("Noch keine Trades im Journal. Übernimm zuerst einen Trade ins Paper Trading und schließe ihn später.")
        return

    df = pd.DataFrame(journal).copy()

    if "symbol" not in df.columns:
        st.warning("Die Journal-Daten sind unvollständig.")
        return

    df["symbol"] = df["symbol"].astype(str)

    if "type" not in df.columns:
        df["type"] = "-"

    if "pnl" not in df.columns:
        df["pnl"] = 0.0

    if "pnl_pct" not in df.columns:
        df["pnl_pct"] = 0.0

    if "main_mistake_type" not in df.columns:
        df["main_mistake_type"] = "-"

    if "main_mistake" not in df.columns:
        df["main_mistake"] = "-"

    if "learning_step" not in df.columns:
        df["learning_step"] = ""

    if "score" not in df.columns:
        df["score"] = 0

    st.caption("Hier siehst du deine abgeschlossenen Trades, typische Fehler und deinen Lernfortschritt.")

    filter_col1, filter_col2 = st.columns(2)

    with filter_col1:
        symbol_options = ["Alle"] + sorted(df["symbol"].dropna().unique().tolist())
        selected_symbol = st.selectbox("Symbol filtern", symbol_options, key="journal_symbol_filter")

    with filter_col2:
        type_options = ["Alle"] + sorted(df["type"].astype(str).dropna().unique().tolist())
        selected_type = st.selectbox("Trade-Typ filtern", type_options, key="journal_type_filter")

    filtered_df = df.copy()

    if selected_symbol != "Alle":
        filtered_df = filtered_df[filtered_df["symbol"] == selected_symbol]

    if selected_type != "Alle":
        filtered_df = filtered_df[filtered_df["type"].astype(str) == selected_type]

    if filtered_df.empty:
        st.warning("Keine Trades für diesen Filter gefunden.")
        return

    trades_count = len(filtered_df)
    winrate = float((filtered_df["pnl"] > 0).mean() * 100) if trades_count > 0 else 0.0
    avg_pnl_pct = float(filtered_df["pnl_pct"].mean()) if "pnl_pct" in filtered_df.columns else 0.0
    total_pnl = float(filtered_df["pnl"].sum()) if "pnl" in filtered_df.columns else 0.0
    avg_score = float(filtered_df["score"].mean()) if "score" in filtered_df.columns else 0.0

    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("Trades", int(trades_count))
    m2.metric("Winrate", f"{winrate:.1f}%")
    m3.metric("Ø PnL %", f"{avg_pnl_pct:.2f}%")
    m4.metric("Gesamt PnL", f"{total_pnl:.2f}")
    m5.metric("Ø Score", f"{avg_score:.1f}")

    st.divider()

    mistake_counter = {}

    if "mistakes" in filtered_df.columns:
        for _, row in filtered_df.iterrows():
            mistakes = row.get("mistakes", [])
            if isinstance(mistakes, list):
                for mistake in mistakes:
                    mistake_counter[mistake] = mistake_counter.get(mistake, 0) + 1

    top_mistakes = sorted(mistake_counter.items(), key=lambda x: x[1], reverse=True)

    st.subheader("Deine häufigsten Fehler")
    if top_mistakes:
        for mistake, count in top_mistakes[:3]:
            if count >= 2:
                st.warning(f"⚠ {mistake} ({count}x)")
            else:
                st.info(f"{mistake} ({count}x)")
    else:
        st.info("Noch nicht genug Daten für eine Fehler-Auswertung.")

    st.divider()

    level_data = _build_level_system(filtered_df)
    progress = _calculate_progress(filtered_df)
    profile = _build_trader_profile(filtered_df)
    learning_goal = _build_next_learning_goal(filtered_df, progress)
    combined = _build_combined_insight(profile, progress)

    st.subheader("Dein Level")

    if level_data["level"] == "Anfänger":
        st.warning(f"Level: {level_data['level']}")
    elif level_data["level"] == "Lernender":
        st.info(f"Level: {level_data['level']}")
    else:
        st.success(f"Level: {level_data['level']}")

    l1, l2 = st.columns(2)
    l1.metric("Level-Punkte", int(level_data["score"]))
    l2.metric("Nächstes Ziel", level_data["next_level"])

    st.progress(min(level_data["score"] / 7, 1.0))
    st.caption(level_data["hint"])

    if learning_goal:
        st.markdown("**Dein Fokus**")
        st.write(learning_goal)

    if profile:
        st.markdown("**Dein Verhalten**")
        st.caption(profile["title"])

    if combined:
        st.markdown("**Kurzfazit**")
        st.write(combined)

    st.divider()

    if "score" in filtered_df.columns and len(filtered_df) > 1:
        st.subheader("Score Entwicklung")
        st.line_chart(filtered_df["score"], use_container_width=True)
        st.divider()

    st.subheader("Letzte Trades kompakt")

    latest_trades = filtered_df.tail(5).iloc[::-1]

    for _, row in latest_trades.iterrows():
        with st.container(border=True):
            top1, top2 = st.columns(2)
            top1.write(f"**{row['symbol']}**")
            top2.write(f"**{row['type']}**")

            mid1, mid2, mid3 = st.columns(3)
            mid1.metric("PnL", f"{float(row['pnl']):.2f}")
            mid2.metric("PnL %", f"{float(row['pnl_pct']):.2f}%")
            mid3.metric("Score", f"{float(row.get('score', 0)):.0f}")

            if str(row.get("main_mistake", "-")) not in ["-", "", "nan", "None"]:
                st.error(f"❗ Wichtigster Fehler: {row['main_mistake']}")

            if str(row.get("learning_step", "")) not in ["", "nan", "None"]:
                st.info(f"📘 Nächster Schritt: {row['learning_step']}")

            if str(row.get("main_mistake_type", "-")) not in ["-", "", "nan", "None"]:
                st.caption(f"Fehler-Typ: {row['main_mistake_type']}")

    st.divider()

    st.subheader("Alle Trades")

    display_cols = [
        col for col in [
            "symbol",
            "type",
            "entry",
            "exit",
            "pnl",
            "pnl_pct",
            "score",
            "signal",
            "risk",
            "trend",
            "main_mistake_type",
        ] if col in filtered_df.columns
    ]

    st.dataframe(filtered_df[display_cols], use_container_width=True)