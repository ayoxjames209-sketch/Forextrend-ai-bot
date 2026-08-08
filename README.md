ForexTrend AI — Telegram Bot (v1)
A Forex assistant bot: live rates, trending pairs, daily analysis, news,
price alerts, favorites, profile, and admin broadcast — with an automatic
daily update job.
What's working in this v1
Feature	Status	Data source
📰 Forex News	✅	NewsAPI.org (needs free key)
🔥 Trending Pairs	✅	Frankfurter.app (free, no key)
📊 Daily Analysis	✅	Frankfurter.app
💱 Live Rates	✅	Frankfurter.app
📅 Economic Calendar	🚧 placeholder	not connected — see note below
🔔 Price Alerts	✅	checked every 5 min via scheduler
⭐ Favorites	✅	SQLite
👤 Profile	✅	SQLite
⏰ Automatic daily updates	✅	APScheduler, default 08:00 UTC
👨‍💻 Admin: broadcast / stats	✅	`/broadcast`, `/stats`
Economic Calendar needs a dedicated data provider (Trading Economics,
FXStreet, Finnhub's economic calendar endpoint, etc.) — most require a paid
or approved API key, so it's stubbed out for now. Tell me which provider
you want and I'll wire up `services/calendar_api.py` the same way the
rates/news services work.
Frankfurter.app covers major/ECB-tracked pairs well but only updates once
per business day (not tick-by-tick). Good enough for v1 trending/analysis;
swap in a paid feed later (e.g. TwelveData, Polygon, Alpha Vantage) if you
need intraday precision — `services/forex_api.py` is the only file you'd
need to touch.
Project structure
```
forextrend-ai-bot/
├── bot.py                 # entry point, wires up all handlers + scheduler
├── config.py               # loads env vars
├── database.py              # SQLite: users, favorites, alerts
├── requirements.txt
├── Procfile
├── .env.example
├── handlers/
│   ├── start.py            # /start + main menu
│   ├── news.py
│   ├── trends.py
│   ├── rates.py
│   ├── analysis.py
│   ├── calendar.py          # placeholder, see note above
│   ├── alerts.py            # includes add-alert conversation flow
│   ├── favorites.py
│   ├── profile.py
│   └── admin.py             # /broadcast, /stats
└── services/
    ├── forex_api.py         # Frankfurter.app wrapper
    ├── news_api.py          # NewsAPI.org wrapper
    └── scheduler.py          # daily update + alert-check jobs
```
Local setup
Create the bot in Telegram
Message @BotFather → `/newbot` → copy the token.
Don't share this token or commit it to GitHub.
Clone / copy this project, then:
```bash
   cd forextrend-ai-bot
   python3 -m venv venv
   source venv/bin/activate        # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   cp .env.example .env
   ```
Fill in `.env`:
`BOT_TOKEN` — from BotFather
`ADMIN_IDS` — your numeric Telegram user ID (get it from @userinfobot)
`NEWS_API_KEY` — free key from newsapi.org (News feature won't return results without it)
Run it:
```bash
   python bot.py
   ```
Open Telegram, message your bot, send `/start`.
Deploying to Railway
Push this project to a GitHub repo (e.g. `forextrend-ai-bot`).
Do not commit your `.env` file — `.gitignore` below covers it.
In Railway: New Project → Deploy from GitHub repo → select the repo.
Go to your Railway service → Variables → add:
`BOT_TOKEN`
`ADMIN_IDS`
`NEWS_API_KEY`
(optionally) `DAILY_UPDATE_HOUR`, `DAILY_UPDATE_MINUTE`
Railway reads `Procfile` and runs `python bot.py` as a worker process — no
web port needed since the bot uses polling, not webhooks.
Deploy. Check the Railway logs for `ForexTrend AI starting (polling mode)...`
Note on the database: `forextrend.db` (SQLite) is written to the
container's local disk, which is ephemeral on Railway — it resets on
every redeploy. That's fine for testing, but for production you'll want
either a Railway volume mounted
at the app's working directory, or to swap SQLite for Railway's managed
Postgres. Say the word and I'll wire in whichever you prefer.
Suggested `.gitignore`
```
venv/
__pycache__/
*.pyc
.env
forextrend.db
```
Next steps (Step 2+ ideas)
Connect a real economic calendar provider
Move from polling to webhooks for lower latency / better Railway fit
Swap SQLite → Postgres for persistent alerts/favorites across redeploys
Add more pairs / user-configurable watchlists
Localize messages for non-English users
