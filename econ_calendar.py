from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

BACK_KB = InlineKeyboardMarkup([[InlineKeyboardButton("⬅ Back to Menu", callback_data="back_menu")]])


async def show_calendar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Placeholder for v1. Economic calendar data (NFP, CPI, rate decisions, etc.)
    needs a dedicated provider — e.g. Trading Economics, FXStreet, or Finnhub's
    /calendar/economic endpoint, most of which require a paid or approved key.
    Wire your chosen provider into services/calendar_api.py and call it here
    the same way news_api.py and forex_api.py are used elsewhere.
    """
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        "📅 <b>Economic Calendar</b>\n\n"
        "Not connected yet — this needs an economic-calendar data provider "
        "(e.g. Trading Economics or Finnhub). Let me know which one you'd "
        "like to use and I'll wire it in as services/calendar_api.py.",
        parse_mode=ParseMode.HTML,
        reply_markup=BACK_KB,
    )
