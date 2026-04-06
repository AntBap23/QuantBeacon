from __future__ import annotations

import discord

from analysis.quant_engine import build_quant_result
from utils.embeds import build_quant_embed


async def handle_quant(interaction: discord.Interaction, symbol: str) -> None:
    await interaction.response.defer(thinking=True)
    try:
        result = await build_quant_result(symbol)
        await interaction.followup.send(embed=build_quant_embed(result))
    except Exception as exc:
        await interaction.followup.send(
            f"Unable to build a quant report for `{symbol.upper()}` right now: {exc}",
            ephemeral=True,
        )

