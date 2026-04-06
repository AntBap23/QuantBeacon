from __future__ import annotations

import os
from urllib.parse import quote_plus

import aiohttp

from utils.types import NewsItem

NEWS_API_URL = "https://newsapi.org/v2/everything"


async def fetch_news(symbol: str, company_name: str | None = None, limit: int = 3) -> list[NewsItem]:
    api_key = os.getenv("NEWS_API_KEY")
    if not api_key:
        raise RuntimeError("NEWS_API_KEY is not configured.")

    query = f'"{company_name}" OR {symbol}' if company_name else symbol
    params = {
        "q": query,
        "language": "en",
        "sortBy": "publishedAt",
        "pageSize": min(limit, 10),
        "apiKey": api_key,
    }

    timeout = aiohttp.ClientTimeout(total=8)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        async with session.get(NEWS_API_URL, params=params) as response:
            response.raise_for_status()
            payload = await response.json()

    articles = payload.get("articles", [])
    return [
        NewsItem(
            title=article.get("title", "Untitled article"),
            url=article.get("url", f"https://news.google.com/search?q={quote_plus(symbol)}"),
            source=article.get("source", {}).get("name", "Unknown"),
            description=article.get("description", "") or "",
            published_at=article.get("publishedAt", "") or "",
        )
        for article in articles[:limit]
    ]


async def fetch_fear_greed() -> tuple[int | None, str]:
    url = "https://api.alternative.me/fng/"
    timeout = aiohttp.ClientTimeout(total=6)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        async with session.get(url) as response:
            response.raise_for_status()
            payload = await response.json()

    data = payload.get("data", [])
    if not data:
        return None, "Unavailable"

    latest = data[0]
    value = int(latest.get("value"))
    label = latest.get("value_classification", "Unknown")
    return value, label

