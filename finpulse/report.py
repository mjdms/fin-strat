from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text

console = Console()

def print_disclaimer():
    disclaimer = """
    [bold red]NOT FINANCIAL ADVICE[/bold red]
    This tool is for educational purposes only. 
    The signals generated are based on mathematical probabilities, ATR volatility, and AI sentiment analysis.
    Do not use this as a sole basis for real trading or investment decisions. You can lose your money.
    """
    console.print(Panel(disclaimer, title="WARNING", border_style="red"))

def print_report(ticker: str, current_price: float, ta_score: float, sentiment_score: float, vol_score: float, signal: str, final_score: float, sl: float, tp1: float, tp2: float):
    print_disclaimer()
    
    # Format sentiment onto a 0-100 scale
    sentiment_mapped = (sentiment_score + 1.0) / 2.0 * 100
    
    table = Table(title=f"FinPulse Core Analysis: {ticker.upper()}")
    
    table.add_column("Metric", justify="left", style="cyan", no_wrap=True)
    table.add_column("Value/Score", justify="right", style="magenta")
    table.add_column("Weight", justify="right", style="green")
    
    table.add_row("Current Price", f"${current_price:.2f}", "-")
    table.add_row("Advanced TA Score", f"{ta_score:.1f}/100", "60%")
    table.add_row("DuckDuckGo Sentiment", f"{sentiment_mapped:.1f}/100", "30%")
    table.add_row("ATR/Volume Score", f"{vol_score:.1f}/100", "10%")
    
    # Signal styling
    if signal == "STRONG BUY":
        signal_style = "bold white on green"
    elif signal == "BUY":
        signal_style = "bold green"
    elif signal == "STRONG SELL":
        signal_style = "bold white on red"
    elif signal == "SELL":
        signal_style = "bold red"
    else:
        signal_style = "bold yellow"
        
    table.add_row("Final Probability Score", f"{final_score:.1f}/100", "100%")
    
    console.print(table)
    console.print(f"\n>> [bold]RECOMMENDATION:[/bold] [{signal_style}] {signal} [/{signal_style}]\n")
    
    # Print Exact Price Targets
    target_table = Table(title="Live Risk Management Targets (Dokładne poziomy)", show_header=True, header_style="bold underline")
    target_table.add_column("Level")
    target_table.add_column("Price Target")
    target_table.add_column("Description")
    
    sl_color = "red" if "BUY" in signal else "green"
    tp_color = "green" if "BUY" in signal else "red"
    
    target_table.add_row(f"[{sl_color}]Stop Loss (SL)[/{sl_color}]", f"${sl:.2f}", "Exit if price crosses this line to prevent major losses.")
    target_table.add_row(f"[{tp_color}]Take Profit 1 (TP1)[/{tp_color}]", f"${tp1:.2f}", "First target to secure baseline profits.")
    target_table.add_row(f"[{tp_color}]Take Profit 2 (TP2)[/{tp_color}]", f"${tp2:.2f}", "Second target for extended structural runs.")
    
    console.print(target_table)
    console.print("\n")
