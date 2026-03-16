# Fin-Strat

A 100% free, local CLI tool for institutional-grade financial analysis. It combines multi-timeframe technical indicators, live news sentiment (processed offline via FinBERT), and automated market screening to help you find the best investment opportunities without needing paid API keys.

## Features
- **Zero API Keys Required**: Uses `yfinance` for prices and `ddgs` for news.
- **Local AI Sentiment**: Analyzes news sentiment on your own machine using HuggingFace's `ProsusAI/finbert` and `DistilBERT`.
- **Institutional Technicals**: Calculates VWAP, Ichimoku Cloud, Supertrend, ATR, and more across Daily and Weekly charts.
- **Automated Market Screener**: Ranks sets of stocks or crypto (e.g., Tech giants, S&P 500, Top 10 Crypto) by their "FinPulse Score".
- **Real-time Signal Scanner**: Monitors a watchlist in the background and alerts you for `STRONG BUY` or `STRONG SELL` signals.
- **Risk Management**: Automatically calculates mathematical Stop-Loss (SL) and Take-Profit (TP) levels based on ATR volatility.

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/mjdms/fin-strat.git
   cd fin-strat
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   .\venv\Scripts\activate  # Windows
   # source venv/bin/activate  # Linux/Mac
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

Fin-Strat comes with several modes:

### 1. Analyze a single asset
Deep dive into a specific ticker:
```bash
python -m finstrat.main analyze AAPL
```
Add `--finbert` to use the more accurate (but slower) financial AI model.

### 2. Market Screener (Leaderboard)
See which stocks are ranked highest in a category:
```bash
python -m finstrat.main screen tech
python -m finstrat.main screen crypto
```

### 3. Background Scanner
Watch multiple stocks for immediate alerts:
```bash
python -m finstrat.main scan AAPL,TSLA,BTC-USD --interval 300
```

### 4. Interactive Mode
Analyze one asset after another without restarting:
```bash
python -m finstrat.main interactive
```

---

## Disclaimer
**NOT FINANCIAL ADVICE.** This tool is for educational and research purposes only. The signals, scores, and price targets generated are based on mathematical probabilities and AI sentiment analysis of public data. Trading financial assets involves significant risk. Never trade more than you can afford to lose.
