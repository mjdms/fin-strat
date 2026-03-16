import pandas as pd
import pandas_ta as ta

def calculate_advanced_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculates advanced multi-timeframe indicators:
    - RSI(14)
    - MACD(12, 26, 9)
    - SMA (50, 200)
    - EMA (20, 50)
    - Bollinger Bands (20, 2)
    - ATR (14)
    - Supertrend (10, 3)
    - Ichimoku Cloud (9, 26, 52)
    """
    df = df.copy()
    
    # Basic Oscillators & Momentum
    df.ta.rsi(length=14, append=True)
    df.ta.macd(fast=12, slow=26, signal=9, append=True)
    
    # Moving Averages
    df.ta.sma(length=50, append=True)
    df.ta.sma(length=200, append=True)
    df.ta.ema(length=20, append=True)
    df.ta.ema(length=50, append=True)
    
    # Volume Weighted Moving Average (Institutional standard)
    df.ta.vwma(length=20, append=True)
    
    # Volatility
    df.ta.bbands(length=20, std=2, append=True)
    df.ta.atr(length=14, append=True)
    
    # Trend (Supertrend)
    # returns SUPERT_10_3.0, SUPERTd_10_3.0 (direction 1/-1), SUPERTl_10_3.0 (long), SUPERTs_10_3.0 (short)
    df.ta.supertrend(length=10, multiplier=3, append=True)
    
    # Ichimoku Cloud
    # returns ISA_9, ISB_26, ITS_9, IKS_26, ICS_26
    df.ta.ichimoku(append=True)
    
    # Handle NaN values for early rows due to moving averages/windows
    df.bfill(inplace=True)
    
    return df
