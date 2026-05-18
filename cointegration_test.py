# cointegration_test.py
# Tests if two stocks are cointegrated (move together over time)

import pandas as pd
import numpy as np
from statsmodels.tsa.stattools import adfuller
from config import TICKER1, TICKER2

def run_adf_test(spread_series):
    """
    Run Augmented Dickey-Fuller test on spread.
    If p-value < 0.05, spread is stationary -> stocks are cointegrated.
    """
    result = adfuller(spread_series.dropna())
    
    adf_statistic = result[0]
    p_value = result[1]
    critical_values = result[4]
    
    return {
        'adf_statistic': adf_statistic,
        'p_value': p_value,
        'critical_values': critical_values,
        'is_stationary': p_value < 0.05
    }

def test_cointegration(df, spread_column='spread'):
    """
    Run cointegration test on the spread.
    Prints results and returns boolean.
    """
    if spread_column not in df.columns:
        print(f"Error: {spread_column} not found in DataFrame")
        return False
    
    spread = df[spread_column]
    result = run_adf_test(spread)
    
    print("\n" + "="*50)
    print("COINTEGRATION TEST RESULTS")
    print("="*50)
    print(f"Stocks tested: {TICKER1} vs {TICKER2}")
    print(f"ADF Statistic: {result['adf_statistic']:.4f}")
    print(f"P-value: {result['p_value']:.6f}")
    print(f"Critical values:")
    for key, value in result['critical_values'].items():
        print(f"  {key}: {value:.4f}")
    print("-"*50)
    
    if result['is_stationary']:
        print("✅ RESULT: Stocks are COINTEGRATED (p < 0.05)")
        print("   The spread is mean-reverting. Pairs trading is valid.")
    else:
        print("❌ RESULT: Stocks are NOT cointegrated (p >= 0.05)")
        print("   The spread may not revert to mean. Choose another pair.")
    
    print("="*50 + "\n")
    
    return result['is_stationary']

def find_best_hedge_ratio(df):
    """
    Find optimal hedge ratio using different methods.
    Returns dictionary with various hedge ratios.
    """
    from sklearn.linear_model import LinearRegression
    
    X = df[TICKER2].values.reshape(-1, 1)
    y = df[TICKER1].values
    
    # Method 1: Ordinary Least Squares
    ols_model = LinearRegression()
    ols_model.fit(X, y)
    ols_ratio = ols_model.coef_[0]
    
    # Method 2: Simple ratio (average of Price1/Price2)
    simple_ratio = (df[TICKER1] / df[TICKER2]).mean()
    
    # Method 3: 1:1 ratio (naive)
    naive_ratio = 1.0
    
    return {
        'ols_ratio': ols_ratio,
        'simple_ratio': simple_ratio,
        'naive_ratio': naive_ratio
    }

if __name__ == "__main__":
    # Test with real data
    from data_fetcher import fetch_pair_data
    from spread_calculator import add_spread_to_dataframe
    
    df = fetch_pair_data()
    if df is not None:
        df = add_spread_to_dataframe(df, use_beta_adjusted=True)
        is_cointegrated = test_cointegration(df)
        
        if is_cointegrated:
            hedge_ratios = find_best_hedge_ratio(df)
            print("Hedge Ratios Found:")
            for method, ratio in hedge_ratios.items():
                print(f"  {method}: {ratio:.4f}")