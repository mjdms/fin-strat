import yfinance as yf
import pandas as pd

def fetch_history(ticker: str, period: str = "2y", interval: str = "1d") -> pd.DataFrame:
    """
    Fetches historical price data from Yahoo Finance.
    Defaults to 2 years to ensure enough data for 200 SMA and Weekly Ichimoku.
    Returns a pandas DataFrame with Open, High, Low, Close, Volume.
    """
    stock = yf.Ticker(ticker)
    df = stock.history(period=period, interval=interval)
    if df.empty:
        raise ValueError(f"Could not fetch data for {ticker}. Ensure the ticker symbol is correct.")
    
    # yfinance sometimes pulls in timezone-aware data, let's normalize the index
    if df.index.tz is not None:
        df.index = df.index.tz_convert(None)
        
    return df

def fetch_multi_timeframe(ticker: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Fetches both daily and weekly data for deep technical analysis.
    """
    df_daily = fetch_history(ticker, period="2y", interval="1d")
    df_weekly = fetch_history(ticker, period="5y", interval="1wk")
    return df_daily, df_weekly
