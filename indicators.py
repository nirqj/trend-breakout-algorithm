import pandas as pd
import numpy as np

# Function to calculate EMA
def calculate_ema(df, period):
    return df['Close'].ewm(span=period, adjust=False).mean()

# Function to detect EMA signals
def detect_ema_signals(df, ema_col, backcandles):
    EMAsignal = [0] * len(df)
    
    for row in range(backcandles, len(df)):
        upt = 1
        dnt = 1
        for i in range(row-backcandles, row+1):
            # Fix the comparison by using direct values instead of __nonzero__
            open_val = df['Open'].values[i]
            close_val = df['Close'].values[i]
            ema_val = df[ema_col].values[i]
            
            if max(open_val, close_val) >= ema_val:
                dnt = 0
            if min(open_val, close_val) <= ema_val:
                upt = 0
                
        if upt == 1 and dnt == 1:
            EMAsignal[row] = 3  # Neither touching the EMA
        elif upt == 1:
            EMAsignal[row] = 2  # All candles above EMA
        elif dnt == 1:
            EMAsignal[row] = 1  # All candles below EMA
    
    return EMAsignal

# Function to detect pivot points
def is_pivot(df, candle_index, window):
    """
    Determine if a candle is a pivot point
    Returns: 1 for pivot high, 2 for pivot low, 3 for both, 0 for neither
    """
    if candle_index - window < 0 or candle_index + window >= len(df):
        return 0
    
    # Get values directly instead of using .iloc
    current_high = df['High'].values[candle_index]
    current_low = df['Low'].values[candle_index]
    
    pivot_high = 1
    pivot_low = 2
    
    # Check surrounding candles
    for i in range(candle_index - window, candle_index + window + 1):
        if i == candle_index:  # Skip comparison with itself
            continue
        if current_low > df['Low'].values[i]:
            pivot_low = 0
        if current_high < df['High'].values[i]:
            pivot_high = 0
    
    if pivot_high and pivot_low:
        return 3
    elif pivot_high:
        return pivot_high
    elif pivot_low:
        return pivot_low
    else:
        return 0

# Function to detect structure patterns
def detect_structure(df, candle_index, backcandles, window):
    """
    Detect support/resistance breakout patterns
    Returns: 0 for no pattern, 1 for support breakout, 2 for resistance breakout
    """
    if (candle_index <= (backcandles + window)) or (candle_index + window + 1 >= len(df)):
        return 0
    
    # Get local data segment without looking ahead
    local_df = df.iloc[candle_index - backcandles - window:candle_index - window].copy()
    
    # Get the last 3 pivot highs and lows
    highs = local_df[local_df['isPivot'] == 1]['High'].tail(3).values
    lows = local_df[local_df['isPivot'] == 2]['Low'].tail(3).values
    
    zone_width = 0.001  # Tolerance for pattern detection
    current_close = df['Close'].values[candle_index]
    
    # Check for support breakout (three similar lows broken downward)
    if len(lows) == 3:
        mean_low = lows.mean()
        support_condition = all(abs(low - mean_low) <= zone_width for low in lows)
        
        if support_condition and (mean_low - current_close) > zone_width * 2:
            return 1  # Support breakout (sell signal)

    # Check for resistance breakout (three similar highs broken upward)
    if len(highs) == 3:
        mean_high = highs.mean()
        resistance_condition = all(abs(high - mean_high) <= zone_width for high in highs)
        
        if resistance_condition and (current_close - mean_high) > zone_width * 2:
            return 2  # Resistance breakout (buy signal)
            
    return 0  # No pattern detected

# Function to generate trading signals
def generate_signals(df):
    # Combine signals from pivot points and pattern detection
    signals = [0] * len(df)
    
    for i in range(len(df)):
        # Buy signal: Pivot low or resistance breakout
        if df['isPivot'].values[i] == 2 or df['pattern_detected'].values[i] == 2:
            signals[i] = 1  # Buy
        
        # Sell signal: Pivot high or support breakout
        elif df['isPivot'].values[i] == 1 or df['pattern_detected'].values[i] == 1:
            signals[i] = -1  # Sell
    
    return signals