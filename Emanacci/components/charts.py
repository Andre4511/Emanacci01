import plotly.graph_objects as go
from plotly.subplots import make_subplots


CHART_BG = "rgba(5, 8, 18, 0.88)"
PLOT_BG = "rgba(5, 8, 18, 0.45)"
GRID_COLOR = "rgba(120, 180, 255, 0.08)"
TEXT_COLOR = "#cfd8ff"
EMA20_COLOR = "#4dabf7"
EMA50_COLOR = "#ffb74d"
RSI_COLOR = "#c084fc"
VOLUME_UP = "rgba(38, 166, 154, 0.55)"
VOLUME_DOWN = "rgba(239, 83, 80, 0.50)"


def _volume_colors(data):
    colors = []
    for open_price, close_price in zip(data["Open"], data["Close"]):
        colors.append(VOLUME_UP if close_price >= open_price else VOLUME_DOWN)
    return colors


def create_main_chart(data, show_ema=True, show_volume=True, show_rsi=False):
    rows = 1
    row_heights = [1.0]

    if show_volume:
        rows += 1
        row_heights.append(0.20)

    if show_rsi:
        rows += 1
        row_heights.append(0.22)

    fig = make_subplots(
        rows=rows,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.04,
        row_heights=row_heights,
    )

    price_row = 1
    volume_row = 2 if show_volume else None
    rsi_row = 3 if show_volume and show_rsi else 2 if show_rsi else None

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
            hovertemplate=(
                "<b>%{x}</b><br>"
                "Open: %{open:.2f}<br>"
                "High: %{high:.2f}<br>"
                "Low: %{low:.2f}<br>"
                "Close: %{close:.2f}<extra></extra>"
            ),
        ),
        row=price_row,
        col=1,
    )

    if show_ema and "EMA20" in data.columns:
        fig.add_trace(
            go.Scatter(
                x=data.index,
                y=data["EMA20"],
                mode="lines",
                name="EMA20",
                line=dict(width=2, color=EMA20_COLOR),
                hovertemplate="EMA20: %{y:.2f}<extra></extra>",
            ),
            row=price_row,
            col=1,
        )

    if show_ema and "EMA50" in data.columns:
        fig.add_trace(
            go.Scatter(
                x=data.index,
                y=data["EMA50"],
                mode="lines",
                name="EMA50",
                line=dict(width=2, color=EMA50_COLOR),
                hovertemplate="EMA50: %{y:.2f}<extra></extra>",
            ),
            row=price_row,
            col=1,
        )

    if show_volume and "Volume" in data.columns and volume_row is not None:
        fig.add_trace(
            go.Bar(
                x=data.index,
                y=data["Volume"],
                name="Volumen",
                marker=dict(color=_volume_colors(data)),
                opacity=0.9,
                hovertemplate="Volumen: %{y:,.0f}<extra></extra>",
            ),
            row=volume_row,
            col=1,
        )

    if show_rsi and "RSI" in data.columns and rsi_row is not None:
        fig.add_trace(
            go.Scatter(
                x=data.index,
                y=data["RSI"],
                mode="lines",
                name="RSI",
                line=dict(width=2, color=RSI_COLOR),
                hovertemplate="RSI: %{y:.2f}<extra></extra>",
            ),
            row=rsi_row,
            col=1,
        )

        fig.add_hline(y=70, line_dash="dash", line_color="rgba(239, 83, 80, 0.7)", row=rsi_row, col=1)
        fig.add_hline(y=30, line_dash="dash", line_color="rgba(38, 166, 154, 0.7)", row=rsi_row, col=1)
        fig.update_yaxes(range=[0, 100], row=rsi_row, col=1)

    fig.update_layout(
        height=760 if show_volume or show_rsi else 560,
        margin=dict(l=8, r=8, t=26, b=8),
        xaxis_rangeslider_visible=False,
        hovermode="x unified",
        paper_bgcolor=CHART_BG,
        plot_bgcolor=PLOT_BG,
        font=dict(color=TEXT_COLOR),
        dragmode="pan",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            bgcolor="rgba(0,0,0,0)",
        ),
    )

    fig.update_xaxes(
        showgrid=True,
        gridcolor=GRID_COLOR,
        zeroline=False,
        showspikes=True,
        spikemode="across",
        spikecolor="rgba(120, 180, 255, 0.25)",
        spikethickness=1,
    )
    fig.update_yaxes(
        showgrid=True,
        gridcolor=GRID_COLOR,
        zeroline=False,
        fixedrange=False,
    )

    return fig