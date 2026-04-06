from __future__ import annotations

import asyncio

from analysis.sentiment import score_news_sentiment
from analysis.technical import compute_30d_volatility, compute_indicators
from data.crypto import fetch_crypto_bundle
from data.news import fetch_fear_greed, fetch_news
from data.stocks import fetch_stock_bundle
from utils.types import AnalysisPayload, QuantResult


def is_crypto_symbol(symbol: str) -> bool:
    return symbol.strip().upper() in {"BTC", "ETH", "SOL", "XRP", "DOGE", "ADA", "AVAX"}


async def fetch_asset_bundle(symbol: str):
    normalized = symbol.strip().upper()
    stock_error: Exception | None = None

    if not is_crypto_symbol(normalized):
        try:
            snapshot, history = await fetch_stock_bundle(normalized)
            if snapshot.price is not None or not history.empty:
                return snapshot, history
        except Exception as exc:
            stock_error = exc

    try:
        return await fetch_crypto_bundle(normalized)
    except Exception:
        if stock_error:
            raise stock_error
        raise


async def build_analysis_payload(symbol: str) -> AnalysisPayload:
    missing_sources: list[str] = []
    snapshot, _history = await fetch_asset_bundle(symbol)

    news_items = []
    try:
        news_items = await fetch_news(snapshot.symbol, snapshot.display_name)
    except Exception:
        missing_sources.append("NewsAPI")

    try:
        sentiment_score, sentiment_label = await score_news_sentiment(news_items)
    except Exception:
        sentiment_score, sentiment_label = None, "Unavailable"
        missing_sources.append("Sentiment")

    try:
        fear_greed_value, fear_greed_label = await fetch_fear_greed()
    except Exception:
        fear_greed_value, fear_greed_label = None, "Unavailable"
        missing_sources.append("Fear & Greed")

    return AnalysisPayload(
        snapshot=snapshot,
        news_items=news_items,
        sentiment_score=sentiment_score,
        sentiment_label=sentiment_label,
        fear_greed_value=fear_greed_value,
        fear_greed_label=fear_greed_label,
        missing_sources=missing_sources,
    )


def _technical_score(indicators: dict[str, object]) -> int:
    score = 50
    rsi = indicators.get("rsi")
    rsi_signal = indicators.get("rsi_signal")
    macd_signal = indicators.get("macd_signal")
    ma_signal = indicators.get("moving_average_signal")
    bollinger_signal = indicators.get("bollinger_signal")
    volume_trend = indicators.get("volume_trend")

    if isinstance(rsi, float):
        if 40 <= rsi <= 60:
            score += 10
        elif 30 <= rsi < 40 or 60 < rsi <= 70:
            score += 3
        else:
            score -= 8

    if rsi_signal == "Oversold":
        score += 8
    elif rsi_signal == "Overbought":
        score -= 8

    score += 12 if macd_signal == "Bullish crossover" else -12

    if ma_signal == "Strong uptrend":
        score += 15
    elif ma_signal == "Above 50D MA":
        score += 8
    elif ma_signal == "Strong downtrend":
        score -= 15
    else:
        score -= 8

    if bollinger_signal == "Below lower band":
        score += 5
    elif bollinger_signal == "Above upper band":
        score -= 5

    if volume_trend == "Above average":
        score += 5

    return max(0, min(100, score))


def _normalize_component(value: float | None) -> int:
    if value is None:
        return 50
    return max(0, min(100, round(value * 100)))


def _fear_greed_component(value: int | None) -> int:
    if value is None:
        return 50
    return max(0, min(100, value))


def _risk_level(volatility: float | None, asset_type: str) -> str:
    if volatility is None:
        return "Unknown"

    thresholds = [20, 35, 55] if asset_type == "stock" else [45, 70, 95]
    if volatility < thresholds[0]:
        return "Low"
    if volatility < thresholds[1]:
        return "Moderate"
    if volatility < thresholds[2]:
        return "High"
    return "Extreme"


def _signal_label(score: int, risk_level: str) -> str:
    if score >= 75 and risk_level in {"Low", "Moderate"}:
        return "STRONG BUY"
    if score >= 60:
        return "CAUTIOUS BUY"
    if score >= 45:
        return "HOLD / WATCH"
    if score >= 30:
        return "REDUCE RISK"
    return "AVOID / WAIT"


async def build_quant_result(symbol: str) -> QuantResult:
    missing_sources: list[str] = []
    snapshot, history = await fetch_asset_bundle(symbol)

    news_task = asyncio.create_task(fetch_news(snapshot.symbol, snapshot.display_name))
    fear_greed_task = asyncio.create_task(fetch_fear_greed())

    news_items: list = []
    try:
        news_items = await news_task
    except Exception:
        missing_sources.append("NewsAPI")

    try:
        sentiment_score, sentiment_label = await score_news_sentiment(news_items)
    except Exception:
        sentiment_score, sentiment_label = None, "Unavailable"
        missing_sources.append("Sentiment")

    try:
        fear_greed_value, fear_greed_label = await fear_greed_task
    except Exception:
        fear_greed_value, fear_greed_label = None, "Unavailable"
        missing_sources.append("Fear & Greed")

    try:
        indicators = await asyncio.to_thread(compute_indicators, history)
        volatility_30d = await asyncio.to_thread(compute_30d_volatility, history)
    except Exception:
        indicators = {
            "rsi": None,
            "rsi_signal": "Unavailable",
            "macd_signal": "Unavailable",
            "bollinger_signal": "Unavailable",
            "moving_average_signal": "Unavailable",
            "volume_trend": "Unavailable",
        }
        volatility_30d = None
        missing_sources.append("Technical indicators")

    technical_score = _technical_score(indicators)
    sentiment_component = _normalize_component(sentiment_score)
    fear_greed_component = _fear_greed_component(fear_greed_value)
    composite_score = round((technical_score * 0.4) + (sentiment_component * 0.4) + (fear_greed_component * 0.2))
    risk_level = _risk_level(volatility_30d, snapshot.asset_type)
    signal = _signal_label(composite_score, risk_level)

    return QuantResult(
        symbol=snapshot.symbol,
        display_name=snapshot.display_name,
        asset_type=snapshot.asset_type,
        rsi=indicators.get("rsi"),
        rsi_signal=str(indicators.get("rsi_signal")),
        macd_signal=str(indicators.get("macd_signal")),
        bollinger_signal=str(indicators.get("bollinger_signal")),
        moving_average_signal=str(indicators.get("moving_average_signal")),
        volume_trend=str(indicators.get("volume_trend")),
        sentiment_score=sentiment_score,
        sentiment_label=sentiment_label,
        fear_greed_value=fear_greed_value,
        fear_greed_label=fear_greed_label,
        technical_score=technical_score,
        composite_score=composite_score,
        risk_level=risk_level,
        volatility_30d=volatility_30d,
        signal=signal,
        price=snapshot.price,
        price_change_pct=snapshot.price_change_pct,
        missing_sources=missing_sources,
    )
