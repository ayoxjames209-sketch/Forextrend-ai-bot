from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

import database as db
from services import forex_api

BACK_KB = InlineKeyboardMarkup([[InlineKeyboardButton("⬅ Back to Menu", callback_data="back_menu")]])


async def show_favorites(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    favorites = db.get_favorites(user_id)

    if not favorites:
        await query.edit_message_text(
            "⭐ You have no favorites yet.\nAdd one from the Live Rates screen.",
            reply_markup=BACK_KB,
        )
        return

    try:
        rates = await forex_api.get_rates(favorites)
    except Exception:
        rates = {}

    lines = ["⭐ <b>Your Favorites</b>\n"]
    for pair in favorites:
        rate = rates.get(pair)
        rate_str = f"{rate:.4f}" if rate is not None else "n/a"
        lines.append(f"• {pair}: {rate_str}")

    kb_rows = [[InlineKeyboardButton(f"🗑 Remove {p}", callback_data=f"fav_del_{p}")] for p in favorites]
    kb_rows.append([InlineKeyboardButton("⬅ Back to Menu", callback_data="back_menu")])

    await query.edit_message_text(
        "\n".join(lines), parse_mode=ParseMode.HTML, reply_markup=InlineKeyboardMarkup(kb_rows)
    )


async def add_favorite(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer("Added to favorites ⭐")
    pair = query.data.replace("fav_add_", "")
    db.add_favorite(query.from_user.id, pair)


async def remove_favorite(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    pair = query.data.replace("fav_del_", "")
    db.remove_favorite(query.from_user.id, pair)
    await query.answer("Removed")
    await show_favorites(update, context)
