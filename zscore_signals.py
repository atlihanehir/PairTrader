# zscore_signals.py
# Calculates z-score and generates trading signals

import pandas as pd
import numpy as np
from config import ZSCORE_ENTRY, ZSCORE_EXIT, STOP_LOSS

def calculate_zscore(spread_series, window=60):
    """
    Calculate z-score using rolling mean and standard deviation.
    Z-score = (current_spread - mean_of_spread) / std_of_spread
    """
    rolling_mean = spread_series.rolling(window=window).mean()
    rolling_std = spread_series.rolling(window=window).std()
    
    zscore = (spread_series - rolling_mean) / rolling_std
    
    return zscore, rolling_mean, rolling_std

def generate_signals(zscore_series):
    """
    Generate trading signals based on z-score thresholds.
    
    Signal values:
    1 = Long position (buy spread, sell hedge)
    -1 = Short position (sell spread, buy hedge)
    0 = No position / Close position
    
    Rules:
    - Enter long when z-score < -ZSCORE_ENTRY
    - Enter short when z-score > ZSCORE_ENTRY  
    - Exit when z-score returns to ZSCORE_EXIT range
    - Emergency stop-loss at STOP_LOSS
    """
    signals = pd.Series(0, index=zscore_series.index)
    position = 0  # 0 = no position, 1 = long, -1 = short
    
    for i, z in enumerate(zscore_series):
        if position == 0:
            # No position - look to enter
            if z < -ZSCORE_ENTRY:
                position = 1  # Long signal
                signals.iloc[i] = 1
            elif z > ZSCORE_ENTRY:
                position = -1  # Short signal
                signals.iloc[i] = -1
                
        elif position == 1:
            # In long position - look to exit or stop-loss
            if abs(z) <= ZSCORE_EXIT:
                position = 0  # Exit
                signals.iloc[i] = 0
            elif z < -STOP_LOSS:
                position = 0  # Emergency stop-loss
                signals.iloc[i] = 0
                print(f"⚠️ STOP LOSS TRIGGERED at z={z:.2f} on {zscore_series.index[i].date()}")
                
        elif position == -1:
            # In short position - look to exit or stop-loss
            if abs(z) <= ZSCORE_EXIT:
                position = 0  # Exit
                signals.iloc[i] = 0
            elif z > STOP_LOSS:
                position = 0  # Emergency stop-loss
                signals.iloc[i] = 0
                print(f"⚠️ STOP LOSS TRIGGERED at z={z:.2f} on {zscore_series.index[i].date()}")
    
    return signals

def add_signals_to_dataframe(df, zscore_column='zscore'):
    """
    Add signal column to DataFrame.
    """
    df_copy = df.copy()
    signals = generate_signals(df_copy[zscore_column])
    df_copy['signal'] = signals
    
    # Count signals
    num_buy = (signals == 1).sum()
    num_sell = (signals == -1).sum()
    num_exits = (signals == 0).sum()
    
    print(f"\nSignal Summary:")
    print(f"  Long signals (buy spread): {num_buy}")
    print(f"  Short signals (sell spread): {num_sell}")
    print(f"  Exit/No position: {num_exits}")
    
    return df_copy

def get_latest_signal(df):
    """
    Get the most recent signal for live trading.
    """
    latest_signal = df['signal'].iloc[-1]
    latest_zscore = df['zscore'].iloc[-1]
    latest_date = df.index[-1]
    
    signal_text = {1: " LONG (Buy spread, sell hedge)", 
                   -1: " SHORT (Sell spread, buy hedge)",
                   0: " NO POSITION / CLOSE"}
    
    print(f"\n{'='*40}")
    print(f"LATEST SIGNAL - {latest_date.date()}")
    print(f"{'='*40}")
    print(f"Z-Score: {latest_zscore:.3f}")
    print(f"Signal: {signal_text[latest_signal]}")
    print(f"{'='*40}")
    
    return latest_signal

if __name__ == "__main__":
    # Test with sample data
    from data_fetcher import fetch_pair_data
    from spread_calculator import add_spread_to_dataframe
    
    df = fetch_pair_data()
    if df is not None:
        df = add_spread_to_dataframe(df)
        
        # Calculate z-score
        zscore, mean, std = calculate_zscore(df['spread'])
        df['zscore'] = zscore
        
        # Add signals
        df = add_signals_to_dataframe(df)
        
        # Show signal dates
        signals_df = df[df['signal'] != 0]
        if len(signals_df) > 0:
            print("\nSignal Dates:")
            for date, row in signals_df.iterrows():
                signal_type = "LONG" if row['signal'] == 1 else "SHORT"
                print(f"  {date.date()}: {signal_type} (z={row['zscore']:.2f})")
