# QuantBeacon

AI market signals in Discord.

QuantBeacon is a Railway-ready Discord bot that pulls live stock and crypto market data, summarizes recent business news, and delivers AI-assisted quant signals through slash commands and Discord embeds.

## Features

- Branded Discord embeds and slash commands built around the QuantBeacon experience
- `/analyze <symbol>` for a quick market snapshot with price, 52-week range, news, sentiment, and risk context
- `/quant <symbol>` for a technical and sentiment-driven quant report with a 0-100 composite score
- `/compare <symbol1> <symbol2>` for side-by-side quant comparisons
- `/help` for a built-in command list
- Partial-failure handling so the bot can still respond when one upstream API is unavailable
- Railway deployment support with `Dockerfile`, `Procfile`, and `railway.toml`

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

Set these in Railway or your local `.env` file:

```env
DISCORD_BOT_TOKEN=your_token_here
DISCORD_GUILD_ID=your_guild_id_here
NEWS_API_KEY=your_newsapi_key_here
USE_FINBERT=false
```

Notes:

- `DISCORD_BOT_TOKEN` comes from the Discord Developer Portal
- `DISCORD_GUILD_ID` is optional but recommended during development for faster slash command sync
- `NEWS_API_KEY` comes from [NewsAPI](https://newsapi.org/)
- `USE_FINBERT=true` enables the heavier Hugging Face sentiment path; leave it `false` for the lightest MVP deploy

## Local Setup

1. Clone the repo.
2. Create and activate a Python 3.11 virtual environment.
3. Install dependencies with `pip install -r requirements.txt`.
4. Copy `.env.example` to `.env` and fill in your values.
5. Run `python main.py`.

## Discord Bot Setup

1. Create a new application in the [Discord Developer Portal](https://discord.com/developers/applications).
2. Add a bot user and copy the bot token into `DISCORD_BOT_TOKEN`.
3. Enable the `applications.commands` scope and the `bot` scope when generating the invite URL.
4. Invite the bot to your server with permissions to view channels, send messages, embed links, and use slash commands.
5. For faster testing, add your server ID to `DISCORD_GUILD_ID`.

## Railway Deployment

1. Fork or clone this repo.
2. Create your Discord bot at `discord.com/developers`.
3. Get a free NewsAPI key.
4. Push the project to GitHub.
5. Connect Railway to the `QuantBeacon` GitHub repo in Railway.
6. Add the environment variables in the Railway dashboard.
7. Railway auto-builds and deploys the bot.
8. Invite the bot to your Discord server.
9. Slash commands should be available immediately after sync.

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

## GitHub + Railway Flow

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

## Invite and Self-Hosting Notes

Anyone can self-host QuantBeacon by setting the required environment variables and running the bot on any Python 3.11-compatible host. Railway is the easiest path because the included deployment files require no extra platform-specific edits beyond adding secrets.

## Contributing

Issues and pull requests are welcome. Keep secrets out of commits, prefer environment variables for configuration, and test slash commands in a development guild before promoting to production.
