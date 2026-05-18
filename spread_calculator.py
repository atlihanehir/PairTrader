# spread_calculator.py
# Calculates spread between two stocks

import pandas as pd
import numpy as np
from config import TICKER1, TICKER2

def calculate_spread(df):
    """
    Calculate the spread between two stocks.
    Simple spread = Price1 - Price2
    """
    spread = df[TICKER1] - df[TICKER2]
    return spread

def calculate_beta_adjusted_spread(df):
    """
    Calculate beta-adjusted spread using linear regression.
    This accounts for different volatilities between stocks.
    """
    from sklearn.linear_model import LinearRegression
    
    X = df[TICKER2].values.reshape(-1, 1)
    y = df[TICKER1].values
    
    model = LinearRegression()
    model.fit(X, y)
    
    beta = model.coef_[0]
    hedge_ratio = beta
    
    # Beta-adjusted spread: Stock1 - (beta * Stock2)
    spread = df[TICKER1] - (hedge_ratio * df[TICKER2])
    
    return spread, hedge_ratio

def add_spread_to_dataframe(df, use_beta_adjusted=False):
    """
    Add spread column to the existing DataFrame.
    """
    df_copy = df.copy()
    
    if use_beta_adjusted:
        spread, hedge_ratio = calculate_beta_adjusted_spread(df)
        df_copy['spread'] = spread
        df_copy['hedge_ratio'] = hedge_ratio
        print(f"Beta-adjusted spread calculated. Hedge ratio: {hedge_ratio:.3f}")
    else:
        spread = calculate_spread(df)
        df_copy['spread'] = spread
        print("Simple spread calculated (Price1 - Price2)")
    
    return df_copy

if __name__ == "__main__":
    # Test with sample data
    from data_fetcher import fetch_pair_data
    
    df = fetch_pair_data()
    if df is not None:
        df_with_spread = add_spread_to_dataframe(df, use_beta_adjusted=True)
        print("\nFirst 5 rows with spread:")
        print(df_with_spread[['KO', 'PEP', 'spread']].head())