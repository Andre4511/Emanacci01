import plotly.graph_objects as go
from plotly.subplots import make_subplots

EMA20_COLOR = "#FFD54F"   # gelb
EMA50_COLOR = "#FF7043"   # orange
EMA200_COLOR = "#AB47BC"  # lila


def create_main_chart(
    data,
    show_ema=True,
    show_volume=True,
    show_rsi=True,
    entry=None,
    stop_loss=None,
    tp1=None,
    tp2=None,
    qty=None,
    risk_amount=None,
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

    # Hauptchart: Candles
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

    # EMAs
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

    current_row = 2

    # Volumen
    if show_volume and "Volume" in data.columns:
        volume_colors = []
        for i in range(len(data)):
            if i == 0:
                volume_colors.append("rgba(79,195,247,0.55)")
            else:
                up = data["Close"].iloc[i] >= data["Close"].iloc[i - 1]
                volume_colors.append("rgba(0,230,118,0.5)" if up else "rgba(255,82,82,0.5)")

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

    # RSI
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

    # =====================
    # TRADE LEVELS
    # =====================

    if entry is not None:
        fig.add_hline(
            y=entry,
            line_color="#4FC3F7",
            line_width=1,
            annotation_text="Entry",
            annotation_position="right",
        )

    if stop_loss is not None:
        fig.add_hline(
            y=stop_loss,
            line_color="#FF5252",
            line_width=1,
            annotation_text="SL",
            annotation_position="right",
        )

    # Entry
    if entry is not None:
        fig.add_hline(
            y=entry,
            line_color="#4FC3F7",
            line_width=1,
            annotation_text="Entry",
            annotation_position="right",
        )

    if stop_loss is not None:
        fig.add_hline(
            y=stop_loss,
            line_color="#FF5252",
            line_width=1,
            annotation_text="SL",
            annotation_position="right",
        )

    if tp1 is not None:
        fig.add_hline(
            y=tp1,
            line_color="rgba(0,230,118,0.8)",
            line_width=1,
            line_dash="dot",
            annotation_text="TP1",
            annotation_position="right",
        )

    if tp2 is not None:
        fig.add_hline(
            y=tp2,
            line_color="rgba(0,230,118,0.5)",
            line_width=1,
            line_dash="dash",
            annotation_text="TP2",
            annotation_position="right",
        )

    # =====================
    # RR ZONE
    # =====================

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

    # =====================
    # RR LABEL
    # =====================

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
                text=f"RR: {rr:.2f}",
                showarrow=False,
                font=dict(size=11, color="#00E676"),
                align="right",
            )

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
                text=f"RR: {rr:.2f}",
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
            text=f"Qty: {qty:.0f}",
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
            text=f"Risk: {risk_amount:.0f} €",
            showarrow=False,
            font=dict(size=11, color="#FF5252"),
            align="right",
        )
    return fig