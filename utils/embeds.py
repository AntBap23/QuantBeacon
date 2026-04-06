from __future__ import annotations

import discord

from utils.branding import BOT_NAME, BOT_TAGLINE
from utils.types import AnalysisPayload, QuantResult


def _fmt_currency(value: float | None, currency: str = "USD") -> str:
    if value is None:
        return "N/A"
    prefix = "$" if currency.upper() == "USD" else f"{currency} "
    return f"{prefix}{value:,.2f}"


def _fmt_pct(value: float | None) -> str:
    if value is None:
        return "N/A"
    sign = "+" if value >= 0 else ""
    return f"{sign}{value:.2f}%"


def _sentiment_percent(value: float | None) -> str:
    if value is None:
        return "N/A"
    return f"{round(value * 100)}%"


def _risk_from_snapshot(change_pct: float | None, asset_type: str) -> str:
    if change_pct is None:
        return "Unknown"
    absolute_change = abs(change_pct)
    thresholds = [2, 4, 7] if asset_type == "stock" else [4, 8, 12]
    if absolute_change < thresholds[0]:
        return "Low"
    if absolute_change < thresholds[1]:
        return "Moderate"
    if absolute_change < thresholds[2]:
        return "High"
    return "Extreme"


def _fmt_rsi(value: float | None) -> str:
    if value is None:
        return "N/A"
    return f"{value:.1f}"


def build_analyze_embed(payload: AnalysisPayload) -> discord.Embed:
    snapshot = payload.snapshot
    embed = discord.Embed(
        title=f"{BOT_NAME} Snapshot — {snapshot.symbol}",
        description=snapshot.display_name,
        color=discord.Color.blurple(),
    )
    embed.add_field(
        name="Price",
        value=f"{_fmt_currency(snapshot.price, snapshot.currency)} | {_fmt_pct(snapshot.price_change_pct)}",
        inline=False,
    )
    embed.add_field(
        name="52W Range",
        value=f"High: {_fmt_currency(snapshot.week_52_high, snapshot.currency)}\nLow: {_fmt_currency(snapshot.week_52_low, snapshot.currency)}",
        inline=True,
    )
    embed.add_field(
        name="Sentiment",
        value=f"{payload.sentiment_label} ({_sentiment_percent(payload.sentiment_score)})",
        inline=True,
    )
    embed.add_field(
        name="Fear & Greed",
        value=(
            f"{payload.fear_greed_value}/100 ({payload.fear_greed_label})"
            if payload.fear_greed_value is not None
            else payload.fear_greed_label
        ),
        inline=True,
    )
    embed.add_field(
        name="Risk Level",
        value=_risk_from_snapshot(snapshot.price_change_pct, snapshot.asset_type),
        inline=True,
    )

    if payload.news_items:
        news_lines = [
            f"[{item.title[:90]}]({item.url})"
            for item in payload.news_items[:3]
        ]
        embed.add_field(name="Top News", value="\n".join(news_lines), inline=False)
    else:
        embed.add_field(name="Top News", value="No recent articles available.", inline=False)

    if payload.missing_sources:
        embed.add_field(
            name="Partial Data Notice",
            value="Unavailable sources: " + ", ".join(sorted(set(payload.missing_sources))),
            inline=False,
        )

    embed.set_footer(text=f"{BOT_TAGLINE} Informational only. Not financial advice.")
    return embed


def build_quant_embed(result: QuantResult) -> discord.Embed:
    embed = discord.Embed(
        title=f"{BOT_NAME} Report — {result.symbol}",
        description=result.display_name,
        color=discord.Color.green() if result.composite_score >= 60 else discord.Color.orange(),
    )
    embed.add_field(
        name="Technical Signals",
        value=(
            f"RSI: {result.rsi:.1f} ({result.rsi_signal})\n"
            f"MACD: {result.macd_signal}\n"
            f"MA Signal: {result.moving_average_signal}\n"
            f"Bollinger: {result.bollinger_signal}\n"
            f"Volume: {result.volume_trend}"
        ) if result.rsi is not None else "Technical data unavailable.",
        inline=False,
    )
    embed.add_field(
        name="Market Mood",
        value=(
            f"Sentiment: {_sentiment_percent(result.sentiment_score)} {result.sentiment_label}\n"
            f"Fear & Greed: "
            f"{result.fear_greed_value if result.fear_greed_value is not None else 'N/A'}"
            f" ({result.fear_greed_label})"
        ),
        inline=False,
    )
    embed.add_field(name="Score", value=f"{result.composite_score}/100", inline=True)
    embed.add_field(name="Risk", value=result.risk_level, inline=True)
    embed.add_field(
        name="30D Volatility",
        value=f"{result.volatility_30d:.2f}%" if result.volatility_30d is not None else "N/A",
        inline=True,
    )
    embed.add_field(name="Signal", value=result.signal, inline=False)

    if result.missing_sources:
        embed.add_field(
            name="Partial Data Notice",
            value="Unavailable sources: " + ", ".join(sorted(set(result.missing_sources))),
            inline=False,
        )

    embed.set_footer(text=f"{BOT_TAGLINE} Not financial advice. DYOR.")
    return embed


def build_compare_embed(left: QuantResult, right: QuantResult) -> discord.Embed:
    embed = discord.Embed(
        title=f"Quant Compare — {left.symbol} vs {right.symbol}",
        color=discord.Color.gold(),
    )
    embed.add_field(
        name=left.symbol,
        value=(
            f"Score: {left.composite_score}/100\n"
            f"Risk: {left.risk_level}\n"
            f"RSI: {_fmt_rsi(left.rsi)}\n"
            f"Signal: {left.signal}"
        ),
        inline=True,
    )
    embed.add_field(
        name=right.symbol,
        value=(
            f"Score: {right.composite_score}/100\n"
            f"Risk: {right.risk_level}\n"
            f"RSI: {_fmt_rsi(right.rsi)}\n"
            f"Signal: {right.signal}"
        ),
        inline=True,
    )
    winner = left if left.composite_score >= right.composite_score else right
    embed.add_field(
        name="Summary",
        value=f"{winner.symbol} currently has the stronger composite setup based on the configured scoring model.",
        inline=False,
    )
    embed.set_footer(text="Scores are model-based summaries, not investment advice.")
    return embed


def build_help_embed() -> discord.Embed:
    embed = discord.Embed(
        title=f"{BOT_NAME} Commands",
        description=BOT_TAGLINE,
        color=discord.Color.blue(),
    )
    embed.add_field(name="/analyze <symbol>", value="Quick snapshot with price, news, and sentiment.", inline=False)
    embed.add_field(name="/quant <symbol>", value="Full quant report with indicators, score, and risk.", inline=False)
    embed.add_field(name="/compare <symbol1> <symbol2>", value="Side-by-side quant comparison.", inline=False)
    embed.add_field(name="/help", value="Show this command guide.", inline=False)
    embed.set_footer(text="Supports stocks via yfinance and major crypto symbols via CoinGecko.")
    return embed
