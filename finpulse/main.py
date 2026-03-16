import typer
import warnings
warnings.filterwarnings("ignore")

from rich.console import Console

from finpulse.scanner import run_analysis, run_scanner
from finpulse.report import print_report

app = typer.Typer(help="FinPulse-Free: Local Market Analysis & Technical Intelligence CLI")
console = Console()

@app.command()
def analyze(
    ticker: str = typer.Argument(..., help="Ticker symbol to analyze (e.g. AAPL, BTC-USD)"),
    finbert: bool = typer.Option(False, "--finbert", help="Use institutional ProsusAI/finbert model instead of DistilBERT")
):
    """
    Perform a deep, multi-timeframe analysis on a single ticker.
    """
    result = run_analysis(ticker, use_finbert=finbert)
    if result:
        ticker, current_price, ta_score, sentiment_score, vol_score, signal, final_score, sl, tp1, tp2 = result
        print_report(ticker, current_price, ta_score, sentiment_score, vol_score, signal, final_score, sl, tp1, tp2)

@app.command()
def scan(
    tickers: str = typer.Argument(..., help="Comma-separated list of tickers (e.g. AAPL,MSFT,TSLA)"),
    interval: int = typer.Option(300, "--interval", "-i", help="Scan interval in seconds (default: 300)")
):
    """
    Run the background scanner to monitor multiple tickers for STRONG BUY/SELL alerts.
    """
    ticker_list = [t.strip().upper() for t in tickers.split(",")]
    run_scanner(ticker_list, interval_seconds=interval)

@app.command()
def screen(
    market: str = typer.Argument("tech", help="Market to screen: 'tech', 'crypto', 'sp500', or comma-separated custom list"),
    finbert: bool = typer.Option(False, "--finbert", help="Use institutional FinBERT model (slower but deeper)")
):
    """
    Autonomously analyzes a bulk list or category, ranks them by score, and prints a sorted leaderboard.
    """
    presets = {
        "tech": ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "TSLA", "META"],
        "crypto": ["BTC-USD", "ETH-USD", "SOL-USD", "ADA-USD", "XRP-USD", "DOGE-USD"],
        "sp500": ["SPY", "JPM", "V", "JNJ", "WMT", "PG", "MA"]
    }
    
    # Check if user typed a category or a custom CSV list
    market_key = market.lower()
    if market_key in presets:
        ticker_list = presets[market_key]
    else:
        ticker_list = [t.strip().upper() for t in market.split(",")]
        
    from finpulse.scanner import run_screener
    run_screener(ticker_list, use_finbert=finbert)

@app.command()
def interactive():
    """
    Launch interactive shell mode to seamlessly analyze stocks without restarting.
    """
    console.print("\n[bold cyan]=== FinPulse Interactive Shell ===[/bold cyan]")
    console.print("Type a ticker to analyze it (e.g. 'AAPL').")
    console.print("Add '--finbert' flag to force heavy NLP (e.g. 'AAPL --finbert').")
    console.print("Type 'quit' or 'exit' to close.\n")
    
    while True:
        try:
            user_input = console.input("[bold green]FinPulse>[/bold green] ").strip()
            if user_input.lower() in ['quit', 'exit']:
                break
                
            if not user_input:
                continue
                
            parts = user_input.split()
            ticker = parts[0].upper()
            use_finbert = "--finbert" in [p.lower() for p in parts]
            
            result = run_analysis(ticker, use_finbert=use_finbert)
            if result:
                _, current_price, ta_score, sentiment_score, vol_score, signal, final_score, sl, tp1, tp2 = result
                print_report(ticker, current_price, ta_score, sentiment_score, vol_score, signal, final_score, sl, tp1, tp2)
                
        except KeyboardInterrupt:
            console.print("\n[yellow]Exiting interactive mode...[/yellow]")
            break

if __name__ == "__main__":
    app()
