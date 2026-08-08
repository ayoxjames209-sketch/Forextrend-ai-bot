from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

import database as db

WELCOME_TEXT = (
    "👋 <b>Welcome to ForexTrend AI</b>\n\n"
    "Your personal Forex market assistant — live rates, trending pairs, "
    "daily analysis, news, and price alerts, all in one place.\n\n"
    "Choose an option below to get started 👇"
)


def main_menu_keyboard() -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton("📰 Forex News", callback_data="menu_news"),
         InlineKeyboardButton("🔥 Trending Pairs", callback_data="menu_trends")],
        [InlineKeyboardButton("📊 Daily Analysis", callback_data="menu_analysis"),
         InlineKeyboardButton("💱 Live Rates", callback_data="menu_rates")],
        [InlineKeyboardButton("📅 Economic Calendar", callback_data="menu_calendar"),
         InlineKeyboardButton("🔔 Price Alerts", callback_data="menu_alerts")],
        [InlineKeyboardButton("⭐ Favorites", callback_data="menu_favorites"),
         InlineKeyboardButton("👤 Profile", callback_data="menu_profile")],
    ]
    return InlineKeyboardMarkup(buttons)


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    db.upsert_user(user.id, user.username or "", user.first_name or "")
    await update.message.reply_text(
        WELCOME_TEXT, parse_mode=ParseMode.HTML, reply_markup=main_menu_keyboard()
    )


async def show_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Used by the 'Back to Menu' button on other screens."""
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        WELCOME_TEXT, parse_mode=ParseMode.HTML, reply_markup=main_menu_keyboard()
    )
