import datetime as dt
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

import config
import database as db

BACK_KB = InlineKeyboardMarkup([[InlineKeyboardButton("⬅ Back to Menu", callback_data="back_menu")]])


async def show_profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    user = db.get_user(user_id)
    favorites = db.get_favorites(user_id)
    alerts = db.get_user_alerts(user_id)

    joined = "unknown"
    if user and user.get("joined_at"):
        joined = dt.datetime.utcfromtimestamp(user["joined_at"]).strftime("%Y-%m-%d")

    is_admin = user_id in config.ADMIN_IDS

    text = (
        "👤 <b>Your Profile</b>\n\n"
        f"Name: {query.from_user.first_name}\n"
        f"Username: @{query.from_user.username or 'n/a'}\n"
        f"User ID: <code>{user_id}</code>\n"
        f"Joined: {joined}\n"
        f"Favorites: {len(favorites)}\n"
        f"Active alerts: {len(alerts)}\n"
        f"Admin: {'Yes' if is_admin else 'No'}"
    )

    await query.edit_message_text(text, parse_mode=ParseMode.HTML, reply_markup=BACK_KB)
