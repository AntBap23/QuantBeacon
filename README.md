# QuantBeacon

AI market signals in Discord.

QuantBeacon is a Railway-ready Discord bot that pulls live stock and crypto market data, summarizes recent business news, and delivers AI-assisted quant signals through slash commands and Discord embeds.

## Features

- `/analyze <symbol>` returns a live snapshot with price, 52-week range, news, sentiment, and risk context
- `/quant <symbol>` returns a technical and sentiment-driven quant report with a 0-100 composite score
- `/compare <symbol1> <symbol2>` compares two assets side by side
- `/help` shows the command list directly inside Discord
- Discord embeds are branded for QuantBeacon instead of plain text output
- Partial-failure handling allows the bot to return usable results even if one upstream API is unavailable
- Railway deployment support is included with `Dockerfile`, `Procfile`, and `railway.toml`

## What Changed

- The project is now fully branded as `QuantBeacon`
- The bot runs through Discord slash commands using `discord.py` 2.x
- Market data is split into dedicated modules for stocks, crypto, news, sentiment, and technical analysis
- The repository includes a GitHub-to-Railway deployment path out of the box
- `.env.example` now documents both required secrets and optional Discord metadata values

## Commands

- `/analyze <symbol>`: Quick snapshot for a stock or major crypto asset
- `/quant <symbol>`: Quant report with RSI, MACD, Bollinger Bands, moving averages, volatility, and composite score
- `/compare <symbol1> <symbol2>`: Side-by-side comparison of two assets using the same scoring model
- `/help`: In-app help menu for end users

## Data Sources

- Stocks and fundamentals: `yfinance`
- Crypto pricing and market data: CoinGecko free API
- Business and financial news: NewsAPI free tier
- Sentiment: TextBlob by default, optional FinBERT via `transformers`
- Fear & Greed Index: alternative.me free API

## Project Structure

```text
QuantBeacon/
├── main.py
├── commands/
├── data/
├── analysis/
├── utils/
├── .env.example
├── requirements.txt
├── Dockerfile
├── railway.toml
├── Procfile
└── README.md
```

## Environment Variables

Set these in Railway or your local `.env` file.

Required for the current code:

```env
DISCORD_BOT_TOKEN=your_token_here
DISCORD_GUILD_ID=your_guild_id_here
NEWS_API_KEY=your_newsapi_key_here
USE_FINBERT=false
```

Optional metadata values you may keep for reference or future extensions:

```env
DISCORD_APPLICATION_ID=your_application_id_here
DISCORD_CLIENT_ID=your_client_id_here
DISCORD_PUBLIC_KEY=your_public_key_here
DISCORD_CHANNEL_ID=your_channel_id_here
```

Notes:

- `DISCORD_BOT_TOKEN` comes from the Discord Developer Portal
- `DISCORD_GUILD_ID` is strongly recommended for development because the bot syncs commands directly to that guild on startup
- `NEWS_API_KEY` comes from [NewsAPI](https://newsapi.org/)
- `USE_FINBERT=true` enables the heavier Hugging Face sentiment path; leave it `false` for the lightest MVP deploy
- CoinGecko and `yfinance` do not require API keys for this MVP
- Never commit your real `.env` file to GitHub

## Discord Setup

1. Create a new application in the [Discord Developer Portal](https://discord.com/developers/applications).
2. Add a bot user under the `Bot` tab.
3. Copy the bot token into `DISCORD_BOT_TOKEN`.
4. Turn on Developer Mode in Discord and copy your server ID into `DISCORD_GUILD_ID`.
5. In `OAuth2 > URL Generator`, select the scopes `bot` and `applications.commands`.
6. Give the bot these permissions:
   - `View Channels`
   - `Send Messages`
   - `Embed Links`
   - `Read Message History`
   - `Use Slash Commands`
7. Invite the bot to your server.

## Self-Hosting

QuantBeacon can be self-hosted on any machine that can run Python 3.11 and stay online continuously.

1. Clone the repo.
2. Create and activate a virtual environment.
3. Install dependencies.
4. Create a `.env` file from `.env.example`.
5. Start the bot.

Example:

```bash
git clone <your-repo-url>
cd QuantBeacon
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python main.py
```

When the bot starts successfully, you should see logs that QuantBeacon synced commands and came online.

## Railway Deployment

Railway is the easiest hosted option for this project because the repository already includes the files Railway expects.

1. Push the QuantBeacon repo to GitHub.
2. Create a new project in Railway.
3. Choose `Deploy from GitHub repo`.
4. Select your QuantBeacon repository.
5. In Railway Variables, add:
   - `DISCORD_BOT_TOKEN`
   - `DISCORD_GUILD_ID`
   - `NEWS_API_KEY`
   - `USE_FINBERT`
6. Railway will build from the included `Dockerfile`.
7. After deploy, confirm the logs show the bot synced and connected.
8. Test `/help`, `/analyze AAPL`, and `/quant BTC` in your Discord server.

Included Railway files:

`railway.toml`:

```toml
[build]
builder = "dockerfile"

[deploy]
restartPolicyType = "on_failure"
restartPolicyMaxRetries = 3
```

`Dockerfile`:

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["python", "main.py"]
```

`Procfile`:

```text
worker: python main.py
```

## GitHub to Railway Flow

Pushes to your GitHub `main` branch can trigger Railway redeploys automatically once the QuantBeacon repo is linked in Railway. No secrets are stored in code; everything is pulled from environment variables with `os.getenv()` and `python-dotenv`.

## How the Bot Works

- Stock snapshots come from `yfinance`
- Crypto snapshots come from CoinGecko market endpoints
- News headlines come from NewsAPI
- Sentiment is averaged across recent headlines
- Technical indicators are computed with `pandas` and `ta`
- Composite quant score weighting:
  - 40% technical signals
  - 40% news sentiment
  - 20% fear/greed index

## Who This Is For

- Use self-hosting if you want full control and already have a VPS, home server, or always-on machine
- Use Railway if you want the fastest path from GitHub to a live Discord bot with minimal infra work
- Use a development guild ID while testing so slash command updates appear faster than global sync

## Contributing

Issues and pull requests are welcome. Keep secrets out of commits, prefer environment variables for configuration, and test slash commands in a development guild before promoting to production.
