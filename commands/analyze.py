from __future__ import annotations

import discord

from analysis.quant_engine import build_analysis_payload
from utils.embeds import build_analyze_embed


async def handle_analyze(interaction: discord.Interaction, symbol: str) -> None:
    await interaction.response.defer(thinking=True)
    try:
        payload = await build_analysis_payload(symbol)
        await interaction.followup.send(embed=build_analyze_embed(payload))
    except Exception as exc:
        await interaction.followup.send(
            f"Unable to analyze `{symbol.upper()}` right now: {exc}",
            ephemeral=True,
        )

