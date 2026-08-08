from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

import config
from services import forex_api

BACK_KB = InlineKeyboardMarkup([[InlineKeyboardButton("⬅ Back to Menu", callback_data="back_menu")]])


async def show_trends(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("🔥 Crunching today's movers...")

    try:
        trending = await forex_api.get_trending(config.MAJOR_PAIRS)
    except Exception:
        await query.edit_message_text(
            "⚠️ Couldn't fetch trending pairs right now. Please try again shortly.",
            reply_markup=BACK_KB,
        )
        return

    lines = ["🔥 <b>Trending Pairs</b>\n"]
    for item in trending:
        arrow = "🟢" if item["pct_change"] >= 0 else "🔴"
        lines.append(f"{arrow} <b>{item['pair']}</b>: {item['rate']:.4f} ({item['pct_change']:+.2f}%)")

    await query.edit_message_text(
        "\n".join(lines), parse_mode=ParseMode.HTML, reply_markup=BACK_KB
    )
