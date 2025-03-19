import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# Import from other modules
from data_handler import get_data
from indicators import calculate_ema, detect_ema_signals, is_pivot, detect_structure, generate_signals
from backtester import backtest_strategy
from visualizer import create_chart

# Set page configuration
st.set_page_config(page_title="Algorithmic Trade", layout="wide")

# Title and description
st.title("Range Breakout Trading System")
st.write("Just choose a ticker, time interval and timeframe, and see the algorithm do magic for you")

# Sidebar for user inputs
st.sidebar.header("Input Parameters")

# User input for stock/forex pair
ticker = st.sidebar.text_input("Enter Stock/Forex Symbol")

# User input for time period
start_date = st.sidebar.date_input("Start Date", datetime.now() - timedelta(days=60))
end_date = st.sidebar.date_input("End Date", datetime.now())

# User input for timeframe
timeframe_options = {
    "1 Day": "1d",
    "1 Week": "1wk",
    "1 Month": "1mo"
}
timeframe = st.sidebar.selectbox("Select Timeframe", list(timeframe_options.keys()))

# User input for strategy parameters
st.sidebar.header("Strategy Parameters")
window = st.sidebar.slider("Pivot Point Window", 3, 20, 10)
backcandles = st.sidebar.slider("Backcandles for EMA Signal", 5, 30, 15)
ema_period = st.sidebar.slider("EMA Period", 50, 300, 150)
pattern_backcandles = st.sidebar.slider("Backcandles for Pattern Detection", 20, 100, 60)
pattern_window = st.sidebar.slider("Window for Pattern Detection", 5, 30, 11)

# User input for risk management
st.sidebar.header("Risk Management")
initial_balance = st.sidebar.number_input("Initial Account Balance", min_value=100.0, value=10000.0, step=1000.0)
risk_percentage = st.sidebar.slider("Risk Percentage per Trade", 0.5, 10.0, 2.0)
stop_loss_percentage = st.sidebar.slider("Stop Loss Percentage", 0.5, 5.0, 2.5)
take_profit_percentage = st.sidebar.slider("Take Profit Percentage", 1.0, 10.0, 5.0)

# Main function to process data and generate signals
def process_data():
    # Download data
    interval = timeframe_options[timeframe]
    df = get_data(ticker, start_date, end_date, interval)
    
    if df is None:
        return None
    
    # Make a copy of dataframe
    df = df.copy()
    
    # Reset index to make it accessible with .iloc
    df = df.reset_index()
    
    # Calculate EMA
    df['EMA'] = calculate_ema(df, ema_period)
    
    # Detect EMA signals
    df['EMASignal'] = detect_ema_signals(df, 'EMA', backcandles)
    
    # Apply pivot detection
    df['isPivot'] = [is_pivot(df, i, window) for i in range(len(df))]
    
    # Apply structure detection
    df['pattern_detected'] = [detect_structure(df, i, pattern_backcandles, pattern_window) for i in range(len(df))]
    
    # Generate trading signals
    df['signal'] = generate_signals(df)
    
    # Set index back to Date for plotting
    df.set_index('Date', inplace=True)
    
    return df

# Main App Logic
st.write("## Data Analysis and Backtesting")

# Add a button to process data and run backtest
if st.button("Load Data and Run Backtest"):
    with st.spinner("Processing data..."):
        # Process data
        df = process_data()
        
        if df is not None:
            # Display data info
            st.write(f"Data loaded: {len(df)} periods from {df.index.min()} to {df.index.max()}")
            
            # Create visualization
            st.write("### Price Chart with Technical Indicators")
            fig = create_chart(df, ticker, ema_period, plot_range=200)
            st.plotly_chart(fig, use_container_width=True)
            
            # Run backtest
            with st.spinner("Running backtest..."):
                trades_df, final_balance = backtest_strategy(
                    df, 
                    initial_balance, 
                    risk_percentage, 
                    stop_loss_percentage, 
                    take_profit_percentage
                )
            
            # Display backtest results
            st.write("### Backtest Results")
            
            # Summary metrics
            st.write("#### Performance Summary")
            col1, col2, col3, col4 = st.columns(4)
            
            # Calculate metrics
            total_trades = len(trades_df)
            if total_trades > 0:
                winning_trades = len(trades_df[trades_df['Profit/Loss Amount'] > 0])
                win_rate = (winning_trades / total_trades) * 100
                total_profit = trades_df['Profit/Loss Amount'].sum()
                profit_percentage = ((final_balance - initial_balance) / initial_balance) * 100
                
                # Fix: Convert numeric values to strings for Streamlit metrics
                col1.metric("Total Trades", str(total_trades))
                col2.metric("Win Rate", f"{win_rate:.2f}%")
                col3.metric("Total Profit/Loss", f"${float(total_profit):.2f}")
                col4.metric("Return", f"{float(profit_percentage):.2f}%")
            else:
                # Define default values when no trades executed
                col1.metric("Total Trades", "0")
                col2.metric("Win Rate", "0.00%")
                col3.metric("Total Profit/Loss", "$0.00")
                col4.metric("Return", "0.00%")
                
                st.write("No trades executed during this period.")
            
            # Trade details
            if total_trades > 0:
                st.write("#### Trade Details")
                
                # Format the trades dataframe for display
                display_df = trades_df.copy()
                display_df['entry_date'] = display_df['Entry Date'].dt.strftime('%Y-%m-%d %H:%M')
                display_df['exit_date'] = display_df['Exit Date'].dt.strftime('%Y-%m-%d %H:%M')
                display_df['profit_loss_percentage'] = display_df['Profit/Loss Percentage'].round(2).astype(str) + '%'
                display_df['profit_loss_amount'] = '$' + display_df['Profit/Loss Amount'].round(2).astype(str)
                display_df['balance'] = '$' + display_df['Balance'].round(2).astype(str)
                
                # Display the trades
                st.dataframe(display_df, use_container_width=True)
                
                # Download button for trade details
                csv = trades_df.to_csv().encode('utf-8')
                st.download_button(
                    "Download Trade History",
                    csv,
                    f"{ticker}_trade_history.csv",
                    "text/csv",
                    key='download-csv'
                )
                
                # Equity curve
                st.write("#### Equity Curve")
                equity_curve = trades_df[['Exit Date', 'Balance']].copy()
                equity_curve = equity_curve.rename(columns={'Exit Date': 'Date'})
                equity_curve.set_index('Date', inplace=True)
                
                import plotly.graph_objects as go
                fig_equity = go.Figure()
                fig_equity.add_trace(go.Scatter(
                    x=equity_curve.index,
                    y=equity_curve['Balance'],
                    mode='lines+markers',
                    name='Account Balance'
                ))
                
                fig_equity.update_layout(
                    title="Account Balance Over Time",
                    xaxis_title="Date",
                    yaxis_title="Balance ($)",
                    height=400
                )
                
                st.plotly_chart(fig_equity, use_container_width=True)
        else:
            st.error("Failed to load data. Please check your input parameters and try again.")

# Add a footer with additional information
st.markdown("---")
st.markdown("""
    **Note:** This is a backtesting system. Past performance may vary with future results. 
    Trade at your own risk.
""")
