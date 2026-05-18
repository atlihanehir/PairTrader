# backtest_engine.py
# Backtests the pairs trading strategy with position sizing and charts

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
from config import INITIAL_CAPITAL, ZSCORE_ENTRY, ZSCORE_EXIT, OUTPUTS_DIR

def run_backtest(df, spread_column='spread', signal_column='signal', position_size_pct=0.1):
    """
    Run backtest with position sizing.
    position_size_pct: Percentage of capital to use per trade (0.1 = 10%)
    """
    capital = INITIAL_CAPITAL
    position = 0  # 0 = no position, 1 = long, -1 = short
    portfolio_value = []
    daily_returns = []
    trades = []
    position_size = 0
    
    for i in range(len(df)):
        signal = df[signal_column].iloc[i]
        price_spread = df[spread_column].iloc[i]
        date = df.index[i]
        
        if signal == 1 and position == 0:
            # Enter LONG position
            position = 1
            position_size = capital * position_size_pct
            entry_price = price_spread
            entry_date = date
            trades.append({
                'type': 'LONG', 
                'entry_date': entry_date, 
                'entry_price': entry_price,
                'position_size': position_size
            })
            capital -= position_size
            
        elif signal == -1 and position == 0:
            # Enter SHORT position
            position = -1
            position_size = capital * position_size_pct
            entry_price = price_spread
            entry_date = date
            trades.append({
                'type': 'SHORT', 
                'entry_date': entry_date, 
                'entry_price': entry_price,
                'position_size': position_size
            })
            capital -= position_size
            
        elif signal == 0 and position != 0:
            # Exit position
            exit_price = price_spread
            exit_date = date
            trade = trades[-1]
            position_size = trade['position_size']
            
            if position == 1:
                # Long position: profit = (exit - entry) * position_size
                profit = (exit_price - trade['entry_price']) * position_size
            else:
                # Short position: profit = (entry - exit) * position_size
                profit = (trade['entry_price'] - exit_price) * position_size
            
            trade['exit_date'] = exit_date
            trade['exit_price'] = exit_price
            trade['profit'] = profit
            trade['profit_pct'] = (profit / position_size) * 100
            capital += position_size + profit
            position = 0
        
        # Track current portfolio value
        current_value = capital
        for trade in trades:
            if 'exit_date' not in trade:
                position_size = trade['position_size']
                if trade['type'] == 'LONG':
                    unrealized = (price_spread - trade['entry_price']) * position_size
                else:
                    unrealized = (trade['entry_price'] - price_spread) * position_size
                current_value += position_size + unrealized
        portfolio_value.append(current_value)
    
    # Calculate daily returns
    portfolio_series = pd.Series(portfolio_value, index=df.index)
    daily_returns = portfolio_series.pct_change().dropna()
    
    # Completed trades only
    completed_trades = [t for t in trades if 'exit_date' in t]
    
    if len(completed_trades) == 0:
        return _empty_results(portfolio_series)
    
    # Calculate metrics
    total_return = ((portfolio_series.iloc[-1] - INITIAL_CAPITAL) / INITIAL_CAPITAL) * 100
    winning_trades = [t for t in completed_trades if t['profit'] > 0]
    win_rate = (len(winning_trades) / len(completed_trades)) * 100
    total_profit = sum(t['profit'] for t in completed_trades)
    avg_profit = total_profit / len(completed_trades)
    
    # Sharpe ratio (annualized)
    sharpe_ratio = (daily_returns.mean() / daily_returns.std()) * (252 ** 0.5) if daily_returns.std() > 0 else 0
    
    # Max drawdown
    rolling_max = portfolio_series.expanding().max()
    drawdown = (portfolio_series - rolling_max) / rolling_max * 100
    max_drawdown = drawdown.min()
    
    # Annualized return
    days = (df.index[-1] - df.index[0]).days
    annualized_return = ((1 + total_return/100) ** (365/days) - 1) * 100 if days > 0 else 0
    
    return {
        'total_return': total_return,
        'annualized_return': annualized_return,
        'num_trades': len(completed_trades),
        'win_rate': win_rate,
        'total_profit': total_profit,
        'avg_profit': avg_profit,
        'sharpe_ratio': sharpe_ratio,
        'max_drawdown': max_drawdown,
        'trades': completed_trades,
        'portfolio_value': portfolio_series,
        'daily_returns': daily_returns
    }

def _empty_results(portfolio_series):
    """Return empty results when no trades completed"""
    return {
        'total_return': 0,
        'annualized_return': 0,
        'num_trades': 0,
        'win_rate': 0,
        'total_profit': 0,
        'avg_profit': 0,
        'sharpe_ratio': 0,
        'max_drawdown': 0,
        'trades': [],
        'portfolio_value': portfolio_series,
        'daily_returns': pd.Series()
    }

def plot_results(df, results, ticker1="KO", ticker2="PEP"):
    """Create and save visualization charts"""
    os.makedirs(OUTPUTS_DIR, exist_ok=True)
    
    # Create figure with 3 subplots
    fig, axes = plt.subplots(3, 1, figsize=(12, 10), sharex=True)
    
    # Plot 1: Spread with z-score thresholds
    ax1 = axes[0]
    ax1.plot(df.index, df['spread'], label='Spread', color='blue', linewidth=1)
    ax1.axhline(y=df['spread'].mean(), color='green', linestyle='--', label='Mean')
    ax1.set_ylabel('Spread (KO - PEP)')
    ax1.set_title(f'Pairs Trading: {ticker1} vs {ticker2}')
    ax1.legend(loc='upper left')
    ax1.grid(True, alpha=0.3)
    
    # Plot 2: Z-score with thresholds
    ax2 = axes[1]
    ax2.plot(df.index, df['zscore'], label='Z-Score', color='purple', linewidth=1)
    ax2.axhline(y=ZSCORE_ENTRY, color='red', linestyle='--', label=f'Entry (+{ZSCORE_ENTRY})')
    ax2.axhline(y=-ZSCORE_ENTRY, color='red', linestyle='--', label=f'Entry (-{ZSCORE_ENTRY})')
    ax2.axhline(y=ZSCORE_EXIT, color='green', linestyle=':', label=f'Exit (±{ZSCORE_EXIT})')
    ax2.axhline(y=-ZSCORE_EXIT, color='green', linestyle=':')
    ax2.axhline(y=0, color='black', linestyle='-', alpha=0.5)
    ax2.set_ylabel('Z-Score')
    ax2.set_title('Z-Score with Trading Thresholds')
    ax2.legend(loc='upper left')
    ax2.grid(True, alpha=0.3)
    
    # Plot 3: Portfolio value
    ax3 = axes[2]
    ax3.plot(results['portfolio_value'].index, results['portfolio_value'], 
             label='Portfolio Value', color='green', linewidth=2)
    ax3.axhline(y=INITIAL_CAPITAL, color='gray', linestyle='--', label=f'Initial (${INITIAL_CAPITAL})')
    ax3.set_xlabel('Date')
    ax3.set_ylabel('Portfolio Value ($)')
    ax3.set_title(f'Portfolio Performance: {results["total_return"]:.2f}% Return')
    ax3.legend(loc='upper left')
    ax3.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    # Save figure
    fig_path = os.path.join(OUTPUTS_DIR, 'backtest_results.png')
    plt.savefig(fig_path, dpi=150, bbox_inches='tight')
    print(f"Chart saved to: {fig_path}")
    
    plt.show()

def print_detailed_results(results):
    """Print formatted detailed backtest results"""
    print("\n" + "="*60)
    print("BACKTEST RESULTS - DETAILED REPORT")
    print("="*60)
    print(f"Initial Capital:     ${INITIAL_CAPITAL:,.2f}")
    print(f"Final Value:         ${results['portfolio_value'].iloc[-1]:,.2f}")
    print(f"Total Return:        {results['total_return']:.2f}%")
    print(f"Annualized Return:   {results['annualized_return']:.2f}%")
    print("-"*60)
    print(f"Number of Trades:    {results['num_trades']}")
    print(f"Winning Trades:      {len([t for t in results['trades'] if t['profit'] > 0])}")
    print(f"Losing Trades:       {len([t for t in results['trades'] if t['profit'] <= 0])}")
    print(f"Win Rate:            {results['win_rate']:.1f}%")
    print("-"*60)
    print(f"Total Profit:        ${results['total_profit']:,.2f}")
    print(f"Average Profit:      ${results['avg_profit']:.2f}")
    print(f"Sharpe Ratio:        {results['sharpe_ratio']:.2f}")
    print(f"Max Drawdown:        {results['max_drawdown']:.2f}%")
    print("="*60)
    
    if results['num_trades'] > 0:
        print("\nTRADE HISTORY:")
        print("-"*60)
        for i, trade in enumerate(results['trades'], 1):
            profit_symbol = "+" if trade['profit'] > 0 else ""
            print(f"{i:2}. {trade['type']:5} | Entry: {trade['entry_date'].date()} @ {trade['entry_price']:8.2f} | "
                  f"Exit: {trade['exit_date'].date()} @ {trade['exit_price']:8.2f} | "
                  f"Profit: {profit_symbol}${trade['profit']:7.2f} ({trade['profit_pct']:.1f}%)")
        print("="*60)

if __name__ == "__main__":
    # Load data
    df = pd.read_csv("data/stock_prices.csv", index_col=0, parse_dates=True)
    
    # Calculate spread
    df['spread'] = df['KO'] - df['PEP']
    
    # Calculate rolling z-score
    window = 60
    rolling_mean = df['spread'].rolling(window=window).mean()
    rolling_std = df['spread'].rolling(window=window).std()
    df['zscore'] = (df['spread'] - rolling_mean) / rolling_std
    
    # Generate signals
    df['signal'] = 0
    df.loc[df['zscore'] > ZSCORE_ENTRY, 'signal'] = -1  # Short
    df.loc[df['zscore'] < -ZSCORE_ENTRY, 'signal'] = 1  # Long
    df.loc[abs(df['zscore']) <= ZSCORE_EXIT, 'signal'] = 0  # Exit
    
    # Run backtest with 10% position sizing
    results = run_backtest(df, position_size_pct=0.1)
    
    # Print results
    print_detailed_results(results)
    
    # Plot charts
    plot_results(df, results)