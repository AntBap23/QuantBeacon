from __future__ import annotations

import math

import pandas as pd
from ta.momentum import RSIIndicator
from ta.trend import EMAIndicator, MACD, SMAIndicator
from ta.volatility import BollingerBands


def prepare_history(history: pd.DataFrame) -> pd.DataFrame:
    if history is None or history.empty:
        raise ValueError("Historical price data is unavailable.")

    df = history.copy()
    rename_map = {}
    for column in df.columns:
        lower = str(column).lower()
        if lower == "close":
            rename_map[column] = "Close"
        elif lower == "volume":
            rename_map[column] = "Volume"
    df = df.rename(columns=rename_map)

    if "Close" not in df.columns:
        raise ValueError("Historical data does not include a Close column.")

    if "Volume" not in df.columns:
        df["Volume"] = pd.NA

    return df.dropna(subset=["Close"])


def compute_indicators(history: pd.DataFrame) -> dict[str, float | str | None]:
    df = prepare_history(history)

    close = df["Close"]
    volume = pd.to_numeric(df["Volume"], errors="coerce")

    rsi = RSIIndicator(close=close, window=14).rsi().iloc[-1]
    macd_indicator = MACD(close=close, window_slow=26, window_fast=12, window_sign=9)
    macd_value = macd_indicator.macd().iloc[-1]
    macd_signal_value = macd_indicator.macd_signal().iloc[-1]
    bb = BollingerBands(close=close, window=20, window_dev=2)
    bb_high = bb.bollinger_hband().iloc[-1]
    bb_low = bb.bollinger_lband().iloc[-1]
    sma_50 = SMAIndicator(close=close, window=50).sma_indicator().iloc[-1] if len(df) >= 50 else None
    sma_200 = SMAIndicator(close=close, window=200).sma_indicator().iloc[-1] if len(df) >= 200 else None
    ema_20 = EMAIndicator(close=close, window=20).ema_indicator().iloc[-1]
    latest_close = close.iloc[-1]
    volume_avg_20 = volume.rolling(20).mean().iloc[-1] if volume.notna().any() else None
    latest_volume = volume.iloc[-1] if volume.notna().any() else None

    if rsi <= 30:
        rsi_signal = "Oversold"
    elif rsi >= 70:
        rsi_signal = "Overbought"
    else:
        rsi_signal = "Neutral"

    macd_signal = "Bullish crossover" if macd_value >= macd_signal_value else "Bearish crossover"

    if latest_close > bb_high:
        bollinger_signal = "Above upper band"
    elif latest_close < bb_low:
        bollinger_signal = "Below lower band"
    else:
        bollinger_signal = "Within bands"

    if sma_50 is not None and sma_200 is not None and latest_close > sma_50 > sma_200:
        moving_average_signal = "Strong uptrend"
    elif sma_50 is not None and sma_200 is not None and latest_close < sma_50 < sma_200:
        moving_average_signal = "Strong downtrend"
    elif sma_50 is not None and latest_close >= sma_50:
        moving_average_signal = "Above 50D MA"
    elif sma_50 is not None:
        moving_average_signal = "Below 50D MA"
    else:
        moving_average_signal = "Insufficient trend history"

    if latest_volume is None or volume_avg_20 is None or math.isnan(volume_avg_20):
        volume_trend = "Unavailable"
    elif latest_volume >= volume_avg_20 * 1.1:
        volume_trend = "Above average"
    elif latest_volume <= volume_avg_20 * 0.9:
        volume_trend = "Below average"
    else:
        volume_trend = "Near average"

    return {
        "rsi": float(rsi),
        "rsi_signal": rsi_signal,
        "macd_signal": macd_signal,
        "bollinger_signal": bollinger_signal,
        "moving_average_signal": moving_average_signal,
        "volume_trend": volume_trend,
        "sma_50": float(sma_50) if sma_50 is not None and pd.notna(sma_50) else None,
        "sma_200": float(sma_200) if sma_200 is not None and pd.notna(sma_200) else None,
        "ema_20": float(ema_20) if pd.notna(ema_20) else None,
    }


def compute_30d_volatility(history: pd.DataFrame) -> float | None:
    df = prepare_history(history)
    returns = df["Close"].pct_change().dropna().tail(30)
    if returns.empty:
        return None
    return float(returns.std() * (252 ** 0.5) * 100)
