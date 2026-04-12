import plotly.graph_objects as go
from plotly.subplots import make_subplots

EMA20_COLOR = "#FFD54F"   # gelb
EMA50_COLOR = "#FF7043"   # orange
EMA200_COLOR = "#AB47BC"  # lila


def create_main_chart(
    data,
    show_ema=True,
    show_volume=True,
    show_rsi=False,
    entry=None,
    stop_loss=None,
    tp1=None,
    tp2=None,
    qty=None,
    risk_amount=None,
    score=None,
    detected_mistakes=None,
    ampel=None,
):
    rows = 1
    row_heights = [1.0]

    if show_volume:
        rows += 1
        row_heights.append(0.22)

    if show_rsi:
        rows += 1
        row_heights.append(0.28)

    fig = make_subplots(
        rows=rows,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.04,
        row_heights=row_heights,
    )

    # =====================================================
    # HAUPTCHART: CANDLES
    # =====================================================
    fig.add_trace(
        go.Candlestick(
            x=data.index,
            open=data["Open"],
            high=data["High"],
            low=data["Low"],
            close=data["Close"],
            name="Preis",
            increasing_line_width=1,
            decreasing_line_width=1,
            increasing_line_color="#00E676",
            decreasing_line_color="#FF5252",
            increasing_fillcolor="#00E676",
            decreasing_fillcolor="#FF5252",
        ),
        row=1,
        col=1,
    )

    # =====================================================
    # EMA LINIEN
    # =====================================================
    if show_ema and "EMA20" in data.columns:
        fig.add_trace(
            go.Scatter(
                x=data.index,
                y=data["EMA20"],
                mode="lines",
                name="EMA20",
                line=dict(color=EMA20_COLOR, width=2),
            ),
            row=1,
            col=1,
        )

    if show_ema and "EMA50" in data.columns:
        fig.add_trace(
            go.Scatter(
                x=data.index,
                y=data["EMA50"],
                mode="lines",
                name="EMA50",
                line=dict(color=EMA50_COLOR, width=2),
            ),
            row=1,
            col=1,
        )

    if show_ema and "EMA200" in data.columns:
        fig.add_trace(
            go.Scatter(
                x=data.index,
                y=data["EMA200"],
                mode="lines",
                name="EMA200",
                line=dict(color=EMA200_COLOR, width=2),
            ),
            row=1,
            col=1,
        )

    # =====================================================
    # TREND-ZONEN
    # =====================================================
    if "EMA20" in data.columns and "EMA50" in data.columns:
        ema20 = data["EMA20"]
        ema50 = data["EMA50"]

        # Grüne Zone zwischen EMA20 und EMA50
        fig.add_trace(
            go.Scatter(
                x=data.index,
                y=ema20,
                mode="lines",
                line=dict(width=0),
                showlegend=False,
                hoverinfo="skip",
            ),
            row=1,
            col=1,
        )

        fig.add_trace(
            go.Scatter(
                x=data.index,
                y=ema50,
                mode="lines",
                fill="tonexty",
                fillcolor="rgba(0,230,118,0.05)",
                line=dict(width=0),
                showlegend=False,
                hoverinfo="skip",
            ),
            row=1,
            col=1,
        )

    current_row = 2

    # =====================================================
    # VOLUMEN
    # =====================================================
    if show_volume and "Volume" in data.columns:
        volume_colors = []

        for i in range(len(data)):
            if i == 0:
                volume_colors.append("rgba(79,195,247,0.55)")
            else:
                up = data["Close"].iloc[i] >= data["Close"].iloc[i - 1]
                volume_colors.append(
                    "rgba(0,230,118,0.5)" if up else "rgba(255,82,82,0.5)"
                )

        fig.add_trace(
            go.Bar(
                x=data.index,
                y=data["Volume"],
                name="Volumen",
                marker_color=volume_colors,
            ),
            row=current_row,
            col=1,
        )
        current_row += 1

    # =====================================================
    # RSI
    # =====================================================
    if show_rsi and "RSI" in data.columns:
        fig.add_trace(
            go.Scatter(
                x=data.index,
                y=data["RSI"],
                mode="lines",
                name="RSI",
                line=dict(color="#4FC3F7", width=2),
            ),
            row=current_row,
            col=1,
        )

        fig.add_hline(
            y=70,
            line_dash="dot",
            line_color="rgba(255,255,255,0.25)",
            row=current_row,
            col=1,
        )
        fig.add_hline(
            y=30,
            line_dash="dot",
            line_color="rgba(255,255,255,0.25)",
            row=current_row,
            col=1,
        )

    # =====================================================
    # LAYOUT
    # =====================================================
    fig.update_layout(
        template="plotly_dark",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=10, r=10, t=10, b=10),
        xaxis_rangeslider_visible=False,
        hovermode="closest",
        dragmode="zoom",
        spikedistance=-1,
        hoverdistance=20,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
        ),
        hoverlabel=dict(
            bgcolor="rgba(15,18,25,0.95)",
            bordercolor="rgba(255,255,255,0.08)",
            font=dict(color="#f5f7fb", size=12),
        ),
    )

    fig.update_xaxes(
        showgrid=False,
        showline=False,
        zeroline=False,
        showspikes=True,
        spikecolor="rgba(255,255,255,0.35)",
        spikethickness=1,
        spikedash="solid",
        spikesnap="hovered data",
        spikemode="across",
    )

    fig.update_yaxes(
        showgrid=True,
        gridcolor="rgba(255,255,255,0.05)",
        zeroline=False,
        showspikes=True,
        spikecolor="rgba(255,255,255,0.35)",
        spikethickness=1,
        spikedash="solid",
        spikesnap="hovered data",
        spikemode="across",
    )

    # =====================================================
    # TRADE LEVELS
    # =====================================================
    if entry is not None:
        fig.add_hline(
            y=entry,
            line_color="#4FC3F7",
            line_width=2,
            annotation_text="Einstieg",
            annotation_position="right",
        )

    if stop_loss is not None:
        fig.add_hline(
            y=stop_loss,
            line_color="#FF5252",
            line_width=2,
            annotation_text="Stop Loss",
            annotation_position="right",
        )

    if tp1 is not None:
        fig.add_hline(
            y=tp1,
            line_color="#00E676",
            line_width=2,
            line_dash="dot",
            annotation_text="Ziel 1",
            annotation_position="right",
        )

    if tp2 is not None:
        fig.add_hline(
            y=tp2,
            line_color="rgba(0,230,118,0.6)",
            line_width=2,
            line_dash="dash",
            annotation_text="Ziel 2",
            annotation_position="right",
        )

    # Entry Marker
    if entry is not None:
        fig.add_trace(
            go.Scatter(
                x=[data.index[-1]],
                y=[entry],
                mode="markers+text",
                marker=dict(
                    size=10,
                    color="#4FC3F7",
                    symbol="circle",
                    line=dict(width=2, color="#ffffff"),
                ),
                text=["Einstieg"],
                textposition="top center",
                showlegend=False,
                hovertemplate="Geplanter Einstieg<extra></extra>",
            ),
            row=1,
            col=1,
        )

    # =====================================================
    # RISIKO-/CHANCE-ZONEN
    # =====================================================
    if entry is not None and stop_loss is not None:
        fig.add_hrect(
            y0=min(entry, stop_loss),
            y1=max(entry, stop_loss),
            fillcolor="rgba(255,82,82,0.12)",
            line_width=0,
            layer="below",
        )

    if entry is not None and tp1 is not None:
        fig.add_hrect(
            y0=min(entry, tp1),
            y1=max(entry, tp1),
            fillcolor="rgba(0,230,118,0.12)",
            line_width=0,
            layer="below",
        )

    # =====================================================
    # RR LABEL
    # =====================================================
    if entry is not None and stop_loss is not None and tp1 is not None:
        risk = abs(entry - stop_loss)
        reward = abs(tp1 - entry)

        if risk > 0:
            rr = reward / risk

            fig.add_annotation(
                xref="paper",
                x=0.99,
                y=tp1,
                yref="y",
                text=f"Chance/Risiko: {rr:.2f}",
                showarrow=False,
                font=dict(size=11, color="#00E676"),
                align="right",
            )

    if qty is not None:
        fig.add_annotation(
            xref="paper",
            x=0.99,
            y=entry if entry is not None else data["Close"].iloc[-1],
            yref="y",
            text=f"Stückzahl: {qty:.0f}",
            showarrow=False,
            font=dict(size=11, color="#f5f7fb"),
            align="right",
        )

    if risk_amount is not None and stop_loss is not None and entry is not None:
        fig.add_annotation(
            xref="paper",
            x=0.99,
            y=stop_loss,
            yref="y",
            text=f"Risiko: {risk_amount:.0f} €",
            showarrow=False,
            font=dict(size=11, color="#FF5252"),
            align="right",
        )

    # =====================================================
    # SMART HINWEIS
    # =====================================================
    if "EMA20" in data.columns and "EMA50" in data.columns:
        ema20_last = float(data["EMA20"].iloc[-1])
        ema50_last = float(data["EMA50"].iloc[-1])
        price_last = float(data["Close"].iloc[-1])

        hint_text = ""
        hint_color = "#f5f7fb"

        if price_last > ema20_last > ema50_last:
            hint_text = "Trend stabil"
            hint_color = "#00E676"
        elif price_last < ema20_last < ema50_last:
            hint_text = "Abwärtstrend aktiv"
            hint_color = "#FF5252"
        else:
            hint_text = "Trend unsicher"
            hint_color = "#FFD54F"

        fig.add_annotation(
            xref="paper",
            x=0.01,
            y=0.98,
            yref="paper",
            text=hint_text,
            showarrow=False,
            font=dict(size=12, color=hint_color),
            align="left",
            bgcolor="rgba(15,18,25,0.7)",
            bordercolor="rgba(255,255,255,0.1)",
            borderwidth=1,
        )

    # =====================================================
    # BESTÄTIGUNGS-SIGNAL
    # =====================================================
    if (
        "Close" in data.columns
        and "EMA20" in data.columns
        and "EMA50" in data.columns
        and len(data) >= 2
    ):
        close_last = float(data["Close"].iloc[-1])
        close_prev = float(data["Close"].iloc[-2])
        ema20_last = float(data["EMA20"].iloc[-1])
        ema50_last = float(data["EMA50"].iloc[-1])

        bullish_confirmation = (
            close_last > ema20_last
            and ema20_last > ema50_last
            and close_last > close_prev
        )

        bearish_warning = (
            close_last < ema20_last
            and ema20_last < ema50_last
            and close_last < close_prev
        )

        if bullish_confirmation:
            fig.add_trace(
                go.Scatter(
                    x=[data.index[-1]],
                    y=[close_last],
                    mode="markers+text",
                    marker=dict(
                        size=12,
                        color="#00E676",
                        symbol="diamond",
                        line=dict(width=1, color="#ffffff"),
                    ),
                    text=["Bestätigung"],
                    textposition="bottom center",
                    showlegend=False,
                    hovertemplate="Mögliche bullische Bestätigung<extra></extra>",
                ),
                row=1,
                col=1,
            )

        elif bearish_warning:
            fig.add_trace(
                go.Scatter(
                    x=[data.index[-1]],
                    y=[close_last],
                    mode="markers+text",
                    marker=dict(
                        size=12,
                        color="#FF5252",
                        symbol="diamond",
                        line=dict(width=1, color="#ffffff"),
                    ),
                    text=["Schwäche"],
                    textposition="bottom center",
                    showlegend=False,
                    hovertemplate="Mögliche bearishe Schwäche<extra></extra>",
                ),
                row=1,
                col=1,
            )

    # =====================================================
    # SMART SCORE HINWEIS
    # =====================================================
    if score is not None:
        score_label = ""
        score_color = "#FFD54F"

        if score >= 75:
            score_label = "Gutes Setup"
            score_color = "#00E676"
        elif score >= 50:
            score_label = "Mit Vorsicht"
            score_color = "#FFD54F"
        else:
            score_label = "Kein gutes Setup"
            score_color = "#FF5252"

        # Trend prüfen
        extra_hint = ""

        if "EMA20" in data.columns and "EMA50" in data.columns:
            ema20 = float(data["EMA20"].iloc[-1])
            ema50 = float(data["EMA50"].iloc[-1])
            price = float(data["Close"].iloc[-1])

            if price > ema20 > ema50:
                extra_hint = "Trend bestätigt"
            elif price < ema20 < ema50:
                extra_hint = "Abwärtstrend"
            else:
                extra_hint = "Trend unklar"

        # Finaler Text
        full_text = f"{score_label} • {score}/100"
        if extra_hint:
            full_text += f"<br><span style='font-size:11px; opacity:0.8'>{extra_hint}</span>"

        fig.add_annotation(
            xref="paper",
            yref="paper",
            x=0.01,
            y=0.90,
            text=full_text,
            showarrow=False,
            font=dict(size=12, color=score_color),
            align="left",
            bgcolor="rgba(15,18,25,0.78)",
            bordercolor="rgba(255,255,255,0.10)",
            borderwidth=1,
        )

    # =====================
    # FEHLER MARKER (KOMPAKT)
    # =====================

    if detected_mistakes:
        short_labels = []

        for mistake in detected_mistakes:
            if "zu früh" in mistake.lower():
                short_labels.append("⚠ Zu früh")
            elif "trend" in mistake.lower():
                short_labels.append("⚠ Trend")
            elif "risiko" in mistake.lower():
                short_labels.append("⚠ Risiko")
            elif "chance-risiko" in mistake.lower():
                short_labels.append("⚠ CRV")
            else:
                short_labels.append("⚠ Hinweis")

        # nur max 3 anzeigen
        short_text = "   ".join(short_labels[:3])

        fig.add_annotation(
            xref="paper",
            yref="paper",
            x=0.02,
            y=0.88,
            text=short_text,
            showarrow=False,
            font=dict(size=12, color="#ffffff"),
            bgcolor="rgba(20,20,20,0.85)",
            bordercolor="rgba(255,255,255,0.1)",
            borderwidth=1,
        )

    # =====================
    # AMPEL BADGE
    # =====================

    if ampel:
        if ampel == "grün":
            text = "🟢 OK"
            color = "rgba(76, 175, 80, 0.9)"
        elif ampel == "gelb":
            text = "🟡 Vorsicht"
            color = "rgba(255, 193, 7, 0.9)"
        else:
            text = "🔴 Risiko"
            color = "rgba(244, 67, 54, 0.9)"

        fig.add_annotation(
            xref="paper",
            yref="paper",
            x=0.98,
            y=0.95,
            text=text,
            showarrow=False,
            align="right",
            font=dict(size=12, color="#ffffff"),
            bgcolor=color,
            bordercolor="rgba(255,255,255,0.1)",
            borderwidth=1,
        )

    return fig