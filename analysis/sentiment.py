from __future__ import annotations

import asyncio
import os
from statistics import mean

from textblob import TextBlob

from utils.types import NewsItem

_FINBERT_PIPELINE = None
_FINBERT_FAILED = False


def _textblob_score(text: str) -> float:
    polarity = TextBlob(text).sentiment.polarity
    return max(0.0, min(1.0, (polarity + 1) / 2))


def _load_finbert():
    global _FINBERT_PIPELINE, _FINBERT_FAILED
    if _FINBERT_PIPELINE or _FINBERT_FAILED:
        return _FINBERT_PIPELINE

    if os.getenv("USE_FINBERT", "false").lower() not in {"1", "true", "yes"}:
        _FINBERT_FAILED = True
        return None

    try:
        from transformers import pipeline

        _FINBERT_PIPELINE = pipeline(
            "text-classification",
            model="ProsusAI/finbert",
            tokenizer="ProsusAI/finbert",
        )
    except Exception:
        _FINBERT_FAILED = True
        return None
    return _FINBERT_PIPELINE


def _finbert_score(text: str) -> float:
    classifier = _load_finbert()
    if not classifier:
        return _textblob_score(text)

    result = classifier(text[:512])[0]
    label = result.get("label", "").lower()
    confidence = float(result.get("score", 0.5))

    if label == "positive":
        return 0.5 + (confidence / 2)
    if label == "negative":
        return 0.5 - (confidence / 2)
    return 0.5


async def score_news_sentiment(news_items: list[NewsItem]) -> tuple[float | None, str]:
    if not news_items:
        return None, "Unavailable"

    texts = [
        ". ".join(part for part in [item.title, item.description] if part).strip()
        for item in news_items
    ]
    texts = [text for text in texts if text]
    if not texts:
        return None, "Unavailable"

    use_finbert = os.getenv("USE_FINBERT", "false").lower() in {"1", "true", "yes"}
    scorer = _finbert_score if use_finbert else _textblob_score
    scores = await asyncio.gather(*(asyncio.to_thread(scorer, text) for text in texts))
    avg_score = mean(scores)

    if avg_score >= 0.67:
        label = "Bullish"
    elif avg_score >= 0.45:
        label = "Neutral"
    else:
        label = "Bearish"
    return avg_score, label

