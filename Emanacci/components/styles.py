# =========================================================
# GLOBAL STYLES (Glass / Dark / Emanacci Look)
# =========================================================

import streamlit as st

def apply_global_style():
    st.markdown("""
        <style>
        /* Gesamter App Hintergrund */
        .stApp {
            background: radial-gradient(
                circle at 20% 0%,
                rgba(79,195,247,0.06),
                transparent 45%
            ),
            radial-gradient(
                circle at 80% 0%,
                rgba(171,71,188,0.06),
                transparent 60%
            ),
            linear-gradient(180deg, #070808 100%, #010526 100%);
        }
                
        /* leichtes Glow in der Mitte */
        .block-container {
            background: radial-gradient(
                circle at top,
                rgba(255,255,255,0.08),
                transparent 60%
            );
        }

        /* Karten */
        div[data-testid="stContainer"] {
            border-radius: 12px;
            padding: 10px;
        }

        /* Buttons */
        .stButton button {
            border-radius: 10px;
            border: 1px solid rgba(255,255,255,0.1);
            background-color: rgba(255,255,255,0.05);
            transition: 0.2s;
        }

        .stButton button:hover {
            background-color: rgba(255,255,255,0.1);
        }

        /* Metrics */
        div[data-testid="metric-container"] {
            background-color: rgba(255,255,255,0.03);
            padding: 10px;
            border-radius: 10px;
        }

        /* Text etwas heller */
        body {
            color: #e6e6e6;
        }
                
        .watchlist-card {
            border: 1px solid rgba(255,255,255,0.08);
            border-radius: 16px;
            padding: 0.7rem 0.8rem 0.5rem 0.8rem;
            background: linear-gradient(180deg, rgba(255,255,255,0.03), rgba(255,255,255,0.015));
            box-shadow: 0 6px 18px rgba(0,0,0,0.22);
            margin-bottom: 0.8rem;
        }

        .watchlist-symbol {
            font-size: 1.05rem;
            font-weight: 700;
            color: #f5f7fb;
            margin-bottom: 0.15rem;
        }

        .watchlist-price {
            font-size: 0.88rem;
            color: rgba(230,230,230,0.78);
            margin-bottom: 0.45rem;
        }
                
        div[data-testid="stPlotlyChart"] {
            padding-top: 0 !important;
            margin-top: -6px !important;
        }
                
        /* Watchlist Card Hover */
        div[data-testid="stContainer"] {
            transition: all 0.2s ease;
        }

        div[data-testid="stContainer"]:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 25px rgba(0,0,0,0.4);
            border-color: rgba(255,255,255,0.15);
        }
                
        /* Sidebar allgemein */
        section[data-testid="stSidebar"] {
            background: linear-gradient(180deg, rgba(8,12,20,0.96), rgba(5,8,15,0.96)) !important;
            border-right: 1px solid rgba(255,255,255,0.06);
        }

        /* Sidebar Buttons */
        section[data-testid="stSidebar"] .stButton button {
            width: 100%;
            justify-content: flex-start;
            text-align: left;
            border-radius: 12px;
            padding: 0.65rem 0.9rem;
            background: rgba(255,255,255,0.03);
            border: 1px solid rgba(255,255,255,0.06);
            margin-bottom: 0.35rem;
        }

        section[data-testid="stSidebar"] .stButton button:hover {
            background: rgba(255,255,255,0.08);
            border-color: rgba(255,255,255,0.12);
        }

        /* Sidebar Überschriften */
        section[data-testid="stSidebar"] h1,
        section[data-testid="stSidebar"] h2,
        section[data-testid="stSidebar"] h3 {
            color: #f5f7fb;
            letter-spacing: 0.02em;
        }
                
        /* Section Cards */
        .em-section-card {
            border: 1px solid rgba(255,255,255,0.07);
            border-radius: 18px;
            padding: 1rem 1rem 0.8rem 1rem;
            background: linear-gradient(180deg, rgba(255,255,255,0.025), rgba(255,255,255,0.015));
            box-shadow: 0 8px 24px rgba(0,0,0,0.22);
            margin-bottom: 1rem;
        }

        .em-section-title {
            font-size: 1.02rem;
            font-weight: 700;
            color: #f5f7fb;
            margin-bottom: 0.2rem;
        }

        .em-section-sub {
            font-size: 0.88rem;
            color: rgba(230,230,230,0.72);
            margin-bottom: 0.9rem;
        }
                
        /* Metrics schöner */
        div[data-testid="metric-container"] {
            background: linear-gradient(180deg, rgba(255,255,255,0.035), rgba(255,255,255,0.02));
            border: 1px solid rgba(255,255,255,0.06);
            border-radius: 14px;
            padding: 0.8rem 0.8rem;
            min-height: 80px;
            display: flex;
            flex-direction: column;
            justify-content: center;
        }

        /* Metric Label */
        div[data-testid="metric-container"] label {
            font-size: 0.75rem;
            color: rgba(230,230,230,0.6);
        }

        /* Metric Value */
        div[data-testid="metric-container"] div {
            font-size: 1.1rem;
            font-weight: 600;
        }
        </style>
    """, unsafe_allow_html=True)