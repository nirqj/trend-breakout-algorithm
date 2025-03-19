import pandas as pd

# Function to backtest the strategy
def backtest_strategy(df, initial_balance, risk_percentage, stop_loss_percentage, take_profit_percentage):
    # Create a copy of the dataframe to avoid modifying the original
    backtest_df = df.copy()
    
    # Initialize trade tracking variables
    balance = initial_balance
    position = 0  # 0: no position, 1: long, -1: short
    entry_price = 0
    entry_date = None
    stop_loss = 0
    take_profit = 0
    trades = []
    position_size = 0
    
    # Loop through the data
    for i in range(1, len(backtest_df)):
        current_date = backtest_df.index[i]
        current_price = backtest_df['Close'].values[i]
        signal = backtest_df['signal'].values[i]
        
        # Check for existing position
        if position != 0:
            # For long positions
            if position == 1:
                # Check if stop loss or take profit hit
                if current_price <= stop_loss or current_price >= take_profit:
                    # Close the position
                    exit_price = current_price
                    profit_loss = (exit_price - entry_price) / entry_price * 100
                    profit_loss_amount = (exit_price - entry_price) * position_size
                    balance += profit_loss_amount
                    
                    # Record the trade
                    trades.append({
                        'Entry Date': entry_date,
                        'Exit Date': current_date,
                        'Position': 'BUY',
                        'Entry Price': entry_price,
                        'Exit Price': exit_price,
                        'Profit/Loss Percentage': profit_loss,
                        'Profit/Loss Amount': profit_loss_amount,
                        'Balance': balance
                    })
                    
                    # Reset position
                    position = 0
            
            # For short positions
            elif position == -1:
                # Check if stop loss or take profit hit
                if current_price >= stop_loss or current_price <= take_profit:
                    # Close the position
                    exit_price = current_price
                    profit_loss = (entry_price - exit_price) / entry_price * 100
                    profit_loss_amount = (entry_price - exit_price) * position_size
                    balance += profit_loss_amount
                    
                    # Record the trade
                    trades.append({
                        'Entry Date': entry_date,
                        'Exit Date': current_date,
                        'Position': 'SELL',
                        'Entry Price': entry_price,
                        'Exit Price': exit_price,
                        'Profit/Loss Percentage': profit_loss,
                        'Profit/Loss Amount': profit_loss_amount,
                        'Balance': balance
                    })
                    
                    # Reset position
                    position = 0
        
        # Check for new signals only if not in a position
        if position == 0 and signal != 0:
            # Calculate position size based on risk percentage
            risk_amount = balance * (risk_percentage / 100)
            
            # Buy signal
            if signal == 1:
                position = 1
                entry_price = current_price
                entry_date = current_date
                stop_loss = entry_price * (1 - stop_loss_percentage / 100)
                take_profit = entry_price * (1 + take_profit_percentage / 100)
                position_size = risk_amount / (entry_price * (stop_loss_percentage / 100))
            
            # Sell signal
            elif signal == -1:
                position = -1
                entry_price = current_price
                entry_date = current_date
                stop_loss = entry_price * (1 + stop_loss_percentage / 100)
                take_profit = entry_price * (1 - take_profit_percentage / 100)
                position_size = risk_amount / (entry_price * (stop_loss_percentage / 100))
    
    # Close any open position at the end
    if position != 0:
        exit_price = backtest_df['Close'].values[-1]
        
        if position == 1:
            profit_loss = (exit_price - entry_price) / entry_price * 100
            profit_loss_amount = (exit_price - entry_price) * position_size
        else:  # position == -1
            profit_loss = (entry_price - exit_price) / entry_price * 100
            profit_loss_amount = (entry_price - exit_price) * position_size
            
        balance += profit_loss_amount
        
        # Record the trade
        trades.append({
            'Entry Date': entry_date,
            'Exit Date': backtest_df.index[-1],
            'Position': 'BUY' if position == 1 else 'SELL',
            'Entry Price': entry_price,
            'Exit Price': exit_price,
            'Profit/Loss Percentage': profit_loss,
            'Profit/Loss Amount': profit_loss_amount,
            'Balance': balance
        })
    
    return pd.DataFrame(trades), balance
