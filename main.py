from __future__ import annotations

import logging
import os

import discord
from discord import app_commands
from dotenv import load_dotenv

from commands.analyze import handle_analyze
from commands.compare import handle_compare
from commands.quant import handle_quant
from utils.embeds import build_help_embed

load_dotenv()
logging.basicConfig(level=logging.INFO)

DISCORD_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
GUILD_ID = os.getenv("DISCORD_GUILD_ID")


class MarketIntelBot(discord.Client):
    def __init__(self) -> None:
        intents = discord.Intents.default()
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self) -> None:
        if GUILD_ID:
            guild = discord.Object(id=int(GUILD_ID))
            self.tree.copy_global_to(guild=guild)
            await self.tree.sync(guild=guild)
            logging.info("Synced slash commands to guild %s", GUILD_ID)
        else:
            await self.tree.sync()
            logging.info("Synced global slash commands")

    async def on_ready(self) -> None:
        logging.info("Bot online as %s (%s)", self.user, self.user.id if self.user else "unknown")


bot = MarketIntelBot()


@bot.tree.command(name="analyze", description="Quick snapshot with price, news, and sentiment")
@app_commands.describe(symbol="Ticker or crypto symbol, e.g. AAPL or BTC")
async def analyze_command(interaction: discord.Interaction, symbol: str) -> None:
    await handle_analyze(interaction, symbol)


@bot.tree.command(name="quant", description="Full quant report with indicators, score, and risk")
@app_commands.describe(symbol="Ticker or crypto symbol, e.g. AAPL or BTC")
async def quant_command(interaction: discord.Interaction, symbol: str) -> None:
    await handle_quant(interaction, symbol)


@bot.tree.command(name="compare", description="Compare two assets side by side")
@app_commands.describe(symbol1="First ticker or crypto symbol", symbol2="Second ticker or crypto symbol")
async def compare_command(interaction: discord.Interaction, symbol1: str, symbol2: str) -> None:
    await handle_compare(interaction, symbol1, symbol2)


@bot.tree.command(name="help", description="List available commands")
async def help_command(interaction: discord.Interaction) -> None:
    await interaction.response.send_message(embed=build_help_embed(), ephemeral=True)


def main() -> None:
    if not DISCORD_TOKEN:
        raise RuntimeError("DISCORD_BOT_TOKEN is required.")
    bot.run(DISCORD_TOKEN, log_handler=None)


if __name__ == "__main__":
    main()

