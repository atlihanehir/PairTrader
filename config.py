# config.py
# Configuration file for PairTrader bot

# Stock pair settings
TICKER1 = "KO"          # First stock (Coca-Cola)
TICKER2 = "PEP"         # Second stock (PepsiCo)

# Date range for data fetching
START_DATE = "2025-01-01"
END_DATE = "2026-06-15"

# Trading parameters
INITIAL_CAPITAL = 10000     # Starting money in dollars
ZSCORE_ENTRY = 2.0          # Buy/sell when z-score exceeds this
ZSCORE_EXIT = 0.5           # Close position when z-score returns here
STOP_LOSS = 3.0             # Emergency exit if z-score hits this

# File paths
DATA_DIR = "data"
OUTPUTS_DIR = "outputs"