import time
import logging
from rich.console import Console

from finpulse.data_fetcher import fetch_multi_timeframe
from finpulse.technical import calculate_advanced_indicators
from finpulse.scrapers import get_live_news
from finpulse.sentiment import analyze_texts
from finpulse.signal_engine import calculate_technical_score, calculate_volume_score, generate_signal, calculate_price_targets
from finpulse.report import print_report

console = Console()

def run_analysis(ticker: str, use_finbert: bool, quiet: bool = False):
    """
    Core analysis execution function. Used by both manual command and background scanner. 
    `quiet` mode suppresses the loading indicators.
    """
    try:
        if not quiet: console.print(f"[bold green]Fetching data for {ticker}...[/bold green]")
        df_daily, df_weekly = fetch_multi_timeframe(ticker)
        
        if not quiet: console.print("[bold cyan]Calculating strict advanced technical indicators...[/bold cyan]")
        df_ta_daily = calculate_advanced_indicators(df_daily)
        df_ta_weekly = calculate_advanced_indicators(df_weekly)
        
        ta_score = calculate_technical_score(df_ta_daily, df_ta_weekly)
        vol_score = calculate_volume_score(df_ta_daily)
        current_price = df_ta_daily.iloc[-1]["Close"]
        
        if not quiet: console.print("[bold yellow]Scraping LIVE news from DuckDuckGo...[/bold yellow]")
        all_texts = get_live_news(ticker, max_results=15)
        
        # Decide if we auto-upgrade to finbert due to low news count
        actual_finbert = use_finbert
        if not use_finbert and len(all_texts) > 0 and len(all_texts) < 5:
            if not quiet: console.print("[yellow]Low news count detected. Auto-upgrading to FinBERT for deeper context.[/yellow]")
            actual_finbert = True
            
        if not quiet: console.print(f"[bold magenta]Running AI sentiment analysis ({'FinBERT' if actual_finbert else 'DistilBERT'})...[/bold magenta]")
        sentiment_score = analyze_texts(all_texts, use_finbert=actual_finbert)
        
        signal, final_score = generate_signal(ta_score, sentiment_score, vol_score)
        sl, tp1, tp2 = calculate_price_targets(df_ta_daily, signal)
        
        return ticker, current_price, ta_score, sentiment_score, vol_score, signal, final_score, sl, tp1, tp2
        
    except Exception as e:
        if not quiet: console.print(f"[bold red]Error analyzing {ticker}: {e}[/bold red]")
        logging.warning(f"Analysis error on {ticker}: {e}")
        return None

def run_scanner(tickers: list[str], interval_seconds: int = 300):
    """
    Background loop that continuously checks a list of tickers every N seconds
    for STRONG BUY or STRONG SELL signals.
    """
    console.print(f"\n[bold blue]=== Starting FinPulse Background Scanner ===[/bold blue]")
    console.print(f"Monitoring: {', '.join(tickers)} every {interval_seconds} seconds.\n")
    
    while True:
        try:
            for ticker in tickers:
                result = run_analysis(ticker, use_finbert=False, quiet=True)
                if result:
                    _, cur_price, _, _, _, signal, _, sl, _, _ = result
                    if signal in ["STRONG BUY", "STRONG SELL"]:
                        color = "green" if signal == "STRONG BUY" else "red"
                        console.print(f"\n🚨 [bold {color}]SCANNER ALERT: {ticker} hit {signal} at ${cur_price:.2f}! SL: ${sl:.2f}[/bold {color}]\n")
            
            # Simple sleep for now. For a robust CLI, this would be an async task.
            console.print(f"[dim]Scanner sleeping for {interval_seconds} seconds...[/dim]")
            time.sleep(interval_seconds)
            
        except KeyboardInterrupt:
            console.print("\n[bold red]Scanner stopped by user![/bold red]")
            break
        except Exception as e:
            console.print(f"[red]Scanner loop error: {e}[/red]")
            time.sleep(60) # fallback delay on network error

def run_screener(tickers: list[str], use_finbert: bool = False):
    """
    Autonomous market screener. Analyzes a batch of tickers, sorts them by their
    Strict Final Score, and prints a beautifully ranked leaderboard with price targets.
    """
    console.print(f"\n[bold cyan]=== FinPulse Autonomous Market Screener ===[/bold cyan]")
    console.print(f"Scanning {len(tickers)} assets in the background. Please wait...\n")
    
    results = []
    
    # Analyze each silently
    for t in tickers:
        res = run_analysis(t, use_finbert=use_finbert, quiet=True)
        if res:
            results.append(res)
            
    if not results:
        console.print("[red]No data could be retrieved for the provided tickers.[/red]")
        return
        
    # Sort by final score (index 6), descending
    results.sort(key=lambda x: x[6], reverse=True)
    
    # Draw leaderboard
    from rich.table import Table
    table = Table(title="Top Investments Leaderboard", show_header=True, header_style="bold underline")
    table.add_column("Rank", justify="center", style="dim")
    table.add_column("Ticker", style="cyan", no_wrap=True)
    table.add_column("Score", justify="right")
    table.add_column("Signal")
    table.add_column("Current")
    table.add_column("Stop Loss")
    table.add_column("Take Profit (TP1)")
    
    for idx, r in enumerate(results):
        ticker, current_price, ta_score, sentiment_score, vol_score, signal, final_score, sl, tp1, tp2 = r
        
        # Color coding the signal
        if "STRONG BUY" in signal:
            sig_fmt = "[bold white on green] STRONG BUY [/]"
        elif "BUY" in signal:
            sig_fmt = "[bold green] BUY [/]"
        elif "STRONG SELL" in signal:
            sig_fmt = "[bold white on red] STRONG SELL [/]"
        elif "SELL" in signal:
            sig_fmt = "[bold red] SELL [/]"
        else:
            sig_fmt = "[bold yellow] HOLD [/]"
            
        score_fmt = f"{final_score:.1f}/100"
        
        table.add_row(
            str(idx + 1),
            ticker,
            score_fmt,
            sig_fmt,
            f"${current_price:.2f}",
            f"${sl:.2f}",
            f"${tp1:.2f}"
        )
        
    console.print(table)
    console.print("\n[dim]* Remember: This is mathematically driven probability, NOT FINANCIAL ADVICE. Always do your own research.[/dim]\n")
