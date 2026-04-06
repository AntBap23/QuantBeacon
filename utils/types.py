from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class NewsItem:
    title: str
    url: str
    source: str
    description: str = ""
    published_at: str = ""


@dataclass(slots=True)
class AssetSnapshot:
    symbol: str
    display_name: str
    asset_type: str
    currency: str
    price: float | None = None
    price_change_pct: float | None = None
    market_cap: float | None = None
    day_volume: float | None = None
    week_52_high: float | None = None
    week_52_low: float | None = None
    extra: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class AnalysisPayload:
    snapshot: AssetSnapshot
    news_items: list[NewsItem]
    sentiment_score: float | None
    sentiment_label: str
    fear_greed_value: int | None
    fear_greed_label: str
    missing_sources: list[str] = field(default_factory=list)


@dataclass(slots=True)
class QuantResult:
    symbol: str
    display_name: str
    asset_type: str
    rsi: float | None
    rsi_signal: str
    macd_signal: str
    bollinger_signal: str
    moving_average_signal: str
    volume_trend: str
    sentiment_score: float | None
    sentiment_label: str
    fear_greed_value: int | None
    fear_greed_label: str
    technical_score: int
    composite_score: int
    risk_level: str
    volatility_30d: float | None
    signal: str
    price: float | None = None
    price_change_pct: float | None = None
    missing_sources: list[str] = field(default_factory=list)

