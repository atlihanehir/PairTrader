# data_fetcher.py
import yfinance as yf
import pandas as pd
import os

# Config degerleri direkt burada tanimla (simdilik)
TICKER1 = "KO"
TICKER2 = "PEP"
START_DATE = "2024-01-01"
END_DATE = "2025-12-31"
DATA_DIR = "data"

def fetch_stock_data(ticker, start_date, end_date):
    print(f"Fetching {ticker}...")
    
    # Veriyi indir
    stock = yf.download(ticker, start=start_date, end=end_date, progress=False)
    
    print(f"  Shape: {stock.shape}")
    print(f"  Columns: {list(stock.columns)}")
    
    # Eger bos geldiyse hata ver
    if stock.empty:
        print(f"  WARNING: No data for {ticker}")
        return None
    
    # Close sutununu al (varsa), yoksa ilk sutunu al
    if 'Close' in stock.columns:
        result = stock['Close']
    else:
        result = stock.iloc[:, 0]  # Ilk sutunu al
    
    print(f"  Got {len(result)} days for {ticker}")
    return result

def fetch_pair_data():
    stock1 = fetch_stock_data(TICKER1, START_DATE, END_DATE)
    stock2 = fetch_stock_data(TICKER2, START_DATE, END_DATE)
    
    if stock1 is None or stock2 is None:
        print("ERROR: Could not fetch data")
        return None
    
    # DataFrame olustur
    df = pd.DataFrame()
    df[TICKER1] = stock1
    df[TICKER2] = stock2
    
    # NaN'lari temizle
    df = df.dropna()
    
    print(f"\nSUCCESS: {len(df)} days of data")
    print(f"Date range: {df.index[0].date()} to {df.index[-1].date()}")
    
    # Klasoru olustur
    os.makedirs(DATA_DIR, exist_ok=True)
    
    # Kaydet
    csv_path = os.path.join(DATA_DIR, "stock_prices.csv")
    df.to_csv(csv_path)
    print(f"Saved to: {csv_path}")
    
    return df

if __name__ == "__main__":
    print("="*50)
    print("PAIRTRADER - DATA FETCHER")
    print("="*50)
    
    result = fetch_pair_data()
    
    if result is not None:
        print("\nFirst 5 rows:")
        print(result.head())
        print("\nLast 5 rows:")
        print(result.tail())
    else:
        print("\nFAILED: Please check your internet connection.")