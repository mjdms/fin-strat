from transformers import pipeline
import torch

# Initialize pipelines lazily to avoid loading models until needed
_distil_analyzer = None
_finbert_analyzer = None

def get_sentiment_analyzer(use_finbert: bool = False):
    global _distil_analyzer, _finbert_analyzer
    
    device = -1
    if torch.cuda.is_available():
        device = 0
    elif hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
        device = "mps"
        
    if use_finbert:
        if _finbert_analyzer is None:
            _finbert_analyzer = pipeline(
                "sentiment-analysis", 
                model="ProsusAI/finbert",
                device=device
            )
        return _finbert_analyzer
    else:
        if _distil_analyzer is None:
            _distil_analyzer = pipeline(
                "sentiment-analysis", 
                model="distilbert-base-uncased-finetuned-sst-2-english",
                device=device
            )
        return _distil_analyzer

def analyze_texts(texts: list[str], use_finbert: bool = False) -> float:
    """
    Takes a list of strings (e.g. news headlines, tweets).
    Returns an average sentiment score strictly between -1.0 (Very Negative) and 1.0 (Very Positive).
    If no texts, returns 0.0 (Neutral).
    """
    if not texts:
        return 0.0
        
    analyzer = get_sentiment_analyzer(use_finbert=use_finbert)
    results = analyzer(texts[:50]) # cap input size to prevent memory overload
    
    total_score = 0.0
    for res in results:
        label = res['label'].lower()
        score = res['score'] # Confidence score usually between 0.5 and 1.0
        
        # Distilbert uses POSITIVE/NEGATIVE, FinBERT uses positive/negative/neutral
        if label == 'positive':
            total_score += score
        elif label == 'negative':
            total_score -= score
        else:
            # Neutral adds nothing to the directional score
            total_score += 0.0
            
    return total_score / len(results)
