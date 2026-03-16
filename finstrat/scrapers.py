from ddgs import DDGS
import logging

def get_live_news(ticker: str, max_results: int = 15) -> list[str]:
    """
    Fetches real-time internet news headlines and snippets for the given ticker
    using DuckDuckGo Search. Only fetches news from the past week (timelimit='w')
    to ensure sentiment is extremely relevant to current price action.
    Returns a list of text strings combining both the title and body snippet.
    """
    texts = []
    try:
        query = f"{ticker} stock news OR crypto market"
        # We use DDGS to securely fetch the latest news articles, strictly within the last 7 days
        with DDGS() as ddgs:
            results = ddgs.news(query, timelimit="w", max_results=max_results)
            if not results:
                # Fallback to general web search if news tab fails, also limited
                results = ddgs.text(query, timelimit="w", max_results=max_results)
                
            for res in results:
                title = res.get("title", "")
                body = res.get("body", "")
                text = f"{title}. {body}"
                texts.append(text)
    except Exception as e:
        logging.warning(f"Could not fetch live DDG news for {ticker}: {e}")
        # Return graceful empty list so signal engine just scores 0 neutral
        
    return texts
