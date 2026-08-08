from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

import config
import database as db
from services import forex_api

BACK_KB = InlineKeyboardMarkup([[InlineKeyboardButton("⬅ Back to Menu", callback_data="back_menu")]])


def pairs_keyboard() -> InlineKeyboardMarkup:
    rows = []
    row = []
    for pair in config.MAJOR_PAIRS:
        row.append(InlineKeyboardButton(pair, callback_data=f"rate_{pair}"))
        if len(row) == 2:
            rows.append(row)
            row = []
    if row:
        rows.append(row)
    rows.append([InlineKeyboardButton("⬅ Back to Menu", callback_data="back_menu")])
    return InlineKeyboardMarkup(rows)


async def show_rates_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        "💱 <b>Live Rates</b>\nChoose a pair to check:",
        parse_mode=ParseMode.HTML,
        reply_markup=pairs_keyboard(),
    )


async def show_single_rate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    pair = query.data.replace("rate_", "")

    try:
        rate = await forex_api.get_rate(pair)
    except Exception:
        rate = None

    if rate is None:
        text = f"⚠️ Couldn't fetch the rate for {pair} right now."
    else:
        base, quote = pair.split("/")
        text = f"💱 <b>{pair}</b>\n1 {base} = {rate:.4f} {quote}"

    star_kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("⭐ Add to Favorites", callback_data=f"fav_add_{pair}")],
        [InlineKeyboardButton("⬅ Back to Rates", callback_data="menu_rates")],
    ])
    await query.edit_message_text(text, parse_mode=ParseMode.HTML, reply_markup=star_kb)
