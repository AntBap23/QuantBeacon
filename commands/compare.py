from __future__ import annotations

import asyncio

import discord

from analysis.quant_engine import build_quant_result
from utils.embeds import build_compare_embed


async def handle_compare(interaction: discord.Interaction, symbol1: str, symbol2: str) -> None:
    await interaction.response.defer(thinking=True)
    try:
        left, right = await asyncio.gather(
            build_quant_result(symbol1),
            build_quant_result(symbol2),
        )
        await interaction.followup.send(embed=build_compare_embed(left, right))
    except Exception as exc:
        await interaction.followup.send(
            f"Unable to compare `{symbol1.upper()}` and `{symbol2.upper()}` right now: {exc}",
            ephemeral=True,
        )

