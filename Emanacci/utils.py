import json
from pathlib import Path

import pandas as pd
import streamlit as st
import yfinance as yf


WATCHLIST_FILE = Path("watchlist.json")
USER_SETTINGS_FILE = Path("user_settings.json")
JOURNAL_NOTES_FILE = Path("trade_journal_notes.json")

def _load_json_file(path: Path, default):
    if path.exists():
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return data
        except Exception:
            return default
    return default


def _save_json_file(path: Path, data):
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        st.warning(f"Speichern fehlgeschlagen: {e}")


def load_trade_journal_notes() -> dict:
    data = _load_json_file(JOURNAL_NOTES_FILE, {})
    return data if isinstance(data, dict) else {}


def save_trade_journal_notes(notes: dict):
    _save_json_file(JOURNAL_NOTES_FILE, notes)


@st.cache_data(show_spinner=False, ttl=300)
def load_data(symbol: str, period: str, interval: str) -> pd.DataFrame:
    symbol = str(symbol).upper().strip()
    period = str(period).strip()
    interval = str(interval).strip()

    # Sichere Kombis für yfinance
    valid_periods_by_interval = {
        "15m": ["1d", "5d", "1mo"],
        "1h": ["5d", "1mo", "3mo", "6mo"],
        "1d": ["1mo", "3mo", "6mo", "1y", "2y", "5y"],
        "1wk": ["6mo", "1y", "2y", "5y"],
    }

    if interval in valid_periods_by_interval:
        if period not in valid_periods_by_interval[interval]:
            period = valid_periods_by_interval[interval][0]

    try:
        data = yf.download(
            symbol,
            period=period,
            interval=interval,
            auto_adjust=True,
            progress=False,
            threads=False,
        )
    except Exception:
        return pd.DataFrame()

    if data is None or data.empty:
        return pd.DataFrame()

    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(0)

    for col in ["Open", "High", "Low", "Close", "Volume"]:
        if col in data.columns:
            data[col] = pd.to_numeric(data[col], errors="coerce")

    required_cols = ["Open", "High", "Low", "Close"]
    data = data.dropna(subset=required_cols)

    return data.copy()


def filter_levels(levels, min_distance_percent: float = 0.01):
    filtered = []

    for level in sorted(levels):
        if not filtered:
            filtered.append(level)
        else:
            too_close = False
            for existing in filtered:
                if abs(level - existing) / existing < min_distance_percent:
                    too_close = True
                    break
            if not too_close:
                filtered.append(level)

    return filtered


def load_watchlist():
    data = _load_json_file(WATCHLIST_FILE, [])

    if isinstance(data, list):
        cleaned = [str(item).upper().strip() for item in data if str(item).strip()]
        return cleaned if cleaned else ["TSLA", "AAPL", "NVDA"]

    return ["TSLA", "AAPL", "NVDA"]


def save_watchlist(watchlist):
    _save_json_file(WATCHLIST_FILE, watchlist)


def calculate_max_drawdown(equity_df: pd.DataFrame) -> float:
    if equity_df.empty or "Equity" not in equity_df.columns:
        return 0.0

    equity_series = equity_df["Equity"].copy()
    running_max = equity_series.cummax()
    drawdown = (equity_series - running_max) / running_max * 100

    return drawdown.min()


def load_user_settings():
    data = _load_json_file(USER_SETTINGS_FILE, {})
    return data if isinstance(data, dict) else {}


def save_user_settings(settings: dict):
    _save_json_file(USER_SETTINGS_FILE, settings)