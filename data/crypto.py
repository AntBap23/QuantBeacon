from __future__ import annotations

from typing import Any

import aiohttp
import pandas as pd

from utils.types import AssetSnapshot

COINGECKO_API = "https://api.coingecko.com/api/v3"

SYMBOL_MAP = {
    "BTC": "bitcoin",
    "ETH": "ethereum",
    "SOL": "solana",
    "XRP": "ripple",
    "DOGE": "dogecoin",
    "ADA": "cardano",
    "AVAX": "avalanche-2",
}


def normalize_crypto_symbol(symbol: str) -> str:
    return symbol.strip().upper()


async def resolve_coin_id(session: aiohttp.ClientSession, symbol: str) -> str:
    normalized = normalize_crypto_symbol(symbol)
    if normalized in SYMBOL_MAP:
        return SYMBOL_MAP[normalized]

    async with session.get(f"{COINGECKO_API}/search", params={"query": normalized}) as response:
        response.raise_for_status()
        payload = await response.json()

    coins = payload.get("coins", [])
    for coin in coins:
        if coin.get("symbol", "").upper() == normalized:
            return coin["id"]
    raise ValueError(f"Unable to resolve crypto symbol '{normalized}' on CoinGecko.")


async def fetch_crypto_bundle(symbol: str) -> tuple[AssetSnapshot, pd.DataFrame]:
    normalized = normalize_crypto_symbol(symbol)
    timeout = aiohttp.ClientTimeout(total=8)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        coin_id = await resolve_coin_id(session, normalized)

        market_params = {"vs_currency": "usd", "ids": coin_id}
        chart_params = {"vs_currency": "usd", "days": "365", "interval": "daily"}

        async with session.get(f"{COINGECKO_API}/coins/markets", params=market_params) as response:
            response.raise_for_status()
            market_payload = await response.json()

        async with session.get(
            f"{COINGECKO_API}/coins/{coin_id}/market_chart",
            params=chart_params,
        ) as response:
            response.raise_for_status()
            chart_payload = await response.json()

    if not market_payload:
        raise ValueError(f"No CoinGecko market data returned for '{normalized}'.")

    market = market_payload[0]
    prices = chart_payload.get("prices", [])
    volumes = chart_payload.get("total_volumes", [])

    rows: list[dict[str, Any]] = []
    for idx, item in enumerate(prices):
        timestamp, close_price = item
        volume = volumes[idx][1] if idx < len(volumes) else None
        rows.append({"timestamp": pd.to_datetime(timestamp, unit="ms"), "Close": close_price, "Volume": volume})

    history = pd.DataFrame(rows)
    if not history.empty:
        history["Date"] = history["timestamp"].dt.date
        history = history.groupby("Date", as_index=False).agg({"Close": "last", "Volume": "last"})
        history["Date"] = pd.to_datetime(history["Date"])
        history = history.set_index("Date")

    snapshot = AssetSnapshot(
        symbol=normalized,
        display_name=market.get("name", normalized),
        asset_type="crypto",
        currency="USD",
        price=market.get("current_price"),
        price_change_pct=market.get("price_change_percentage_24h"),
        market_cap=market.get("market_cap"),
        day_volume=market.get("total_volume"),
        week_52_high=history["Close"].max() if not history.empty else None,
        week_52_low=history["Close"].min() if not history.empty else None,
        extra={"coin_id": coin_id, "ath": market.get("ath"), "atl": market.get("atl")},
    )
    return snapshot, history

