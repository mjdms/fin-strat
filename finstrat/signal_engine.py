import pandas as pd

def calculate_technical_score(df_daily: pd.DataFrame, df_weekly: pd.DataFrame) -> float:
    """
    Returns an advanced accuracy score 0-100 based on Daily and Weekly charts.
    Uses Supertrend, Ichimoku, EMA/SMA crossings, RSI, and MACD.
    """
    d_latest = df_daily.iloc[-1]
    d_prev = df_daily.iloc[-2]
    w_latest = df_weekly.iloc[-1]
    
    score = 50.0 # Neutral start
    
    # --- 1. Weekly Macro Trend (Very Important, handles big structural bias) ---
    w_close = w_latest.get("Close", 0)
    w_sma50 = w_latest.get("SMA_50", w_close)
    w_super_dir = w_latest.get(f"SUPERTd_{10}_{3.0}", 0)  # 1 for bull, -1 for bear
    
    # Heavy penalty for fighting the macro trend
    if w_close < w_sma50 or w_super_dir == -1:
         score -= 20   # Macro bear trend
    elif w_close > w_sma50 and w_super_dir == 1:
         score += 20   # Macro bull trend
         
    # --- 2. Daily Trend & Momentum (Supertrend & Moving Averages) ---
    d_close = d_latest.get("Close", 0)
    d_ema20 = d_latest.get("EMA_20", 0)
    d_ema50 = d_latest.get("EMA_50", 0)
    d_super_dir = d_latest.get(f"SUPERTd_{10}_{3.0}", 0)
    
    if d_close > d_ema20 > d_ema50:
        score += 15 # Strong short-term alignment
    elif d_close < d_ema20 < d_ema50:
        score -= 15
        
    if d_super_dir == 1:
        score += 10
    elif d_super_dir == -1:
        score -= 10
        
    vwma_20 = d_latest.get("VWMA_20", d_close)
    if d_close > vwma_20:
        score += 10 # Bullish institutional flow
    elif d_close < vwma_20:
        score -= 10 # Bearish institutional flow
        
    # --- 3. Ichimoku Cloud (Support/Resistance) ---
    isa_9 = d_latest.get("ISA_9", 0)
    isb_26 = d_latest.get("ISB_26", 0)
    cloud_top = max(isa_9, isb_26)
    cloud_bot = min(isa_9, isb_26)
    
    if d_close > cloud_top:
        score += 15 # Above cloud (Bullish)
    elif d_close < cloud_bot:
        score -= 15 # Below cloud (Bearish)
        
    # --- 4. RSI & MACD Over-extensions (Mean Reversion/Momentum) ---
    rsi = d_latest.get("RSI_14", 50)
    if rsi < 30:
        score += 10  # Oversold bounce chance
    elif rsi > 70:
        score -= 10  # Overbought pullback risk
        
    macd = d_latest.get("MACDh_12_26_9", 0) # MACD Histogram
    prev_macd = d_prev.get("MACDh_12_26_9", 0)
    if macd > 0 and prev_macd <= 0:
        score += 10  # Bull cross
    elif macd < 0 and prev_macd >= 0:
        score -= 10  # Bear cross
        
    # --- 5. Bollinger Bands (Extreme exhaustions) ---
    bb_lower = d_latest.get("BBL_20_2.0", d_close)
    bb_upper = d_latest.get("BBU_20_2.0", d_close)
    
    if d_close <= bb_lower:
        score += 5  # Price bouncing off lower band
    elif d_close >= bb_upper:
        score -= 5  # Price rejecting off upper band
        
    return max(0.0, min(100.0, score))

def calculate_volume_score(df_daily: pd.DataFrame) -> float:
    latest = df_daily.iloc[-1]
    avg_vol = df_daily["Volume"].rolling(window=20).mean().iloc[-1]
    
    atr = latest.get("ATR_14", 0)
    daily_range = latest["High"] - latest["Low"]
    is_atr_breakout = daily_range > (atr * 1.5)
    
    if latest["Volume"] > avg_vol * 1.5 and latest["Close"] > latest["Open"] and is_atr_breakout:
        return 100.0
    elif latest["Volume"] > avg_vol * 1.5 and latest["Close"] < latest["Open"] and is_atr_breakout:
        return 0.0
    return 50.0

def calculate_price_targets(df_daily: pd.DataFrame, signal: str) -> tuple[float, float, float]:
    """
    Calculates exact risk-management targets (dokładnie do ilu wzrośnie/spadnie).
    Returns (StopLoss, TakeProfit1, TakeProfit2)
    """
    latest = df_daily.iloc[-1]
    current_price = latest["Close"]
    atr = latest.get("ATR_14", current_price * 0.02) # Default 2% if missing
    
    # 1.5 ATR for Stop Loss, 2.0 ATR for TP1, 3.5 ATR for TP2
    if 'BUY' in signal:
        sl_price = current_price - (atr * 1.5)
        tp1_price = current_price + (atr * 2.0)
        tp2_price = current_price + (atr * 3.5)
    elif 'SELL' in signal:
        sl_price = current_price + (atr * 1.5)
        tp1_price = current_price - (atr * 2.0)
        tp2_price = current_price - (atr * 3.5)
    else: # HOLD
        sl_price = current_price - (atr * 1.0) # Tight stop
        tp1_price = current_price + (atr * 1.0)
        tp2_price = current_price + (atr * 2.0)
        
    return sl_price, tp1_price, tp2_price

def generate_signal(ta_score: float, sentiment_score: float, vol_score: float) -> tuple[str, float]:
    sentiment_mapped = (sentiment_score + 1.0) / 2.0 * 100
    final_score = (ta_score * 0.60) + (sentiment_mapped * 0.30) + (vol_score * 0.10)
    
    if final_score >= 75:
        return "STRONG BUY", final_score
    elif final_score >= 60:
        return "BUY", final_score
    elif final_score <= 25:
        return "STRONG SELL", final_score
    elif final_score <= 40:
        return "SELL", final_score
    return "HOLD", final_score
