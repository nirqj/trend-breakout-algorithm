import plotly.graph_objects as go

def create_chart(df, ticker, ema_period, plot_range=200):
    # Select a slice of data for visualization
    if len(df) > plot_range:
        df_plot = df.iloc[-plot_range:]
    else:
        df_plot = df
    
    # Create figure
    fig = go.Figure()
    
    # Add candlestick chart
    fig.add_trace(go.Candlestick(
        x=df_plot.index,
        open=df_plot['Open'],
        high=df_plot['High'],
        low=df_plot['Low'],
        close=df_plot['Close'],
        name="Price",
        increasing=dict(line=dict(color='green'), fillcolor='green'),  # Bullish candles
        decreasing=dict(line=dict(color='red'), fillcolor='red')        # Bearish candles
    ))
    
    # Add EMA line
    fig.add_trace(go.Scatter(
        x=df_plot.index,
        y=df_plot['EMA'],
        line=dict(color='blue', width=1),
        name=f"EMA {ema_period}"
    ))
    
    # Add pivot points
    pivot_highs = df_plot[df_plot['isPivot'] == 1]
    pivot_lows = df_plot[df_plot['isPivot'] == 2]
    
    # Add pivot highs
    if not pivot_highs.empty:
        fig.add_trace(go.Scatter(
            x=pivot_highs.index,
            y=pivot_highs['High'] * 1.001,  # Offset for visibility (1% above the high)
            mode="markers",
            marker=dict(symbol="triangle-down", size=10, color="red"),
            name="Pivot High"
        ))
    
    # Add pivot lows
    if not pivot_lows.empty:
        fig.add_trace(go.Scatter(
            x=pivot_lows.index,
            y=pivot_lows['Low'] * 0.999,  # Offset for visibility (1% below the low)
            mode="markers",
            marker=dict(symbol="triangle-up", size=10, color="green"),
            name="Pivot Low"
        ))
    
    # Add pattern detection markers
    support_breaks = df_plot[df_plot['pattern_detected'] == 1]
    resistance_breaks = df_plot[df_plot['pattern_detected'] == 2]
    
    # Add support break markers
    if not support_breaks.empty:
        fig.add_trace(go.Scatter(
            x=support_breaks.index,
            y=support_breaks['Low'] * 0.99,  # Offset for visibility (1% below the low)
            mode="markers",
            marker=dict(symbol="star", size=12, color="red"),
            name="Support Break (Sell)"
        ))
    
    # Add resistance break markers
    if not resistance_breaks.empty:
        fig.add_trace(go.Scatter(
            x=resistance_breaks.index,
            y=resistance_breaks['High'] * 1.01,  # Offset for visibility (1% above the high)
            mode="markers",
            marker=dict(symbol="star", size=12, color="green"),
            name="Resistance Break (Buy)"
        ))
    
    # Configure layout
    fig.update_layout(
        title=f"{ticker} Price with Technical Analysis",
        xaxis_title="Date",
        yaxis_title="Price",
        xaxis_rangeslider_visible=False,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        height=600
    )
    
    return fig