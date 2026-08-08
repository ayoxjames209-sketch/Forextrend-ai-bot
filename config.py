"""
Central configuration for ForexTrend AI.
All values are loaded from environment variables (.env locally, Railway
"Variables" tab in production). Never hard-code secrets here.
"""
import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

_admin_raw = os.getenv("ADMIN_IDS", "")
ADMIN_IDS = [int(x.strip()) for x in _admin_raw.split(",") if x.strip().isdigit()]

NEWS_API_KEY = os.getenv("NEWS_API_KEY", "")

DATABASE_PATH = os.getenv("DATABASE_PATH", "forextrend.db")

DAILY_UPDATE_HOUR = int(os.getenv("DAILY_UPDATE_HOUR", "8"))
DAILY_UPDATE_MINUTE = int(os.getenv("DAILY_UPDATE_MINUTE", "0"))

ALERT_CHECK_INTERVAL_MINUTES = int(os.getenv("ALERT_CHECK_INTERVAL_MINUTES", "5"))

# Major pairs shown across the bot (Trending, Rates, Analysis)
MAJOR_PAIRS = [
    "EUR/USD", "GBP/USD", "USD/JPY", "USD/CHF",
    "AUD/USD", "USD/CAD", "NZD/USD",
]

if not BOT_TOKEN:
    raise RuntimeError(
        "BOT_TOKEN is not set. Create a .env file locally (see .env.example) "
        "or add BOT_TOKEN as a Railway environment variable."
    )
