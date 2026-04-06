from __future__ import annotations

import asyncio
from dataclasses import asdict

import pandas as pd
import yfinance as yf

from utils.types import AssetSnapshot


def _normalize_symbol(symbol: str) -> str:
    return symbol.strip().upper()


def _load_ticker_payload(symbol: str) -> tuple[AssetSnapshot, pd.DataFrame]:
    normalized = _normalize_symbol(symbol)
    ticker = yf.Ticker(normalized)
    history = ticker.history(period="1y", interval="1d", auto_adjust=False)
    info = ticker.fast_info or {}
    full_info = ticker.info or {}

    display_name = full_info.get("shortName", normalized)
    price = info.get("lastPrice") or info.get("regularMarketPrice")
    previous_close = info.get("previousClose")
    change_pct = None
    if price is not None and previous_close:
        change_pct = ((price - previous_close) / previous_close) * 100

    snapshot = AssetSnapshot(
        symbol=normalized,
        display_name=display_name or normalized,
        asset_type="stock",
        currency=info.get("currency", "USD"),
        price=price,
        price_change_pct=change_pct,
        market_cap=info.get("marketCap"),
        day_volume=info.get("lastVolume"),
        week_52_high=info.get("yearHigh"),
        week_52_low=info.get("yearLow"),
        extra={
            "exchange": info.get("exchange"),
            "sector": full_info.get("sector"),
        },
    )
    return snapshot, history


async def fetch_stock_snapshot(symbol: str) -> AssetSnapshot:
    snapshot, _ = await asyncio.to_thread(_load_ticker_payload, symbol)
    return snapshot


async def fetch_stock_history(symbol: str) -> pd.DataFrame:
    _, history = await asyncio.to_thread(_load_ticker_payload, symbol)
    return history


async def fetch_stock_bundle(symbol: str) -> tuple[AssetSnapshot, pd.DataFrame]:
    return await asyncio.to_thread(_load_ticker_payload, symbol)


def snapshot_to_dict(snapshot: AssetSnapshot) -> dict:
    return asdict(snapshot)
