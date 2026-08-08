from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

import config
from services import forex_api

BACK_KB = InlineKeyboardMarkup([[InlineKeyboardButton("⬅ Back to Menu", callback_data="back_menu")]])


async def show_analysis(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("📊 Building today's market summary...")

    try:
        trending = await forex_api.get_trending(config.MAJOR_PAIRS)
    except Exception:
        await query.edit_message_text(
            "⚠️ Couldn't build the analysis right now. Please try again shortly.",
            reply_markup=BACK_KB,
        )
        return

    gainers = [t for t in trending if t["pct_change"] > 0]
    losers = [t for t in trending if t["pct_change"] < 0]

    lines = ["📊 <b>Daily Market Analysis</b>\n"]
    lines.append(f"Pairs tracked: {len(trending)}")
    lines.append(f"🟢 Gainers: {len(gainers)}   🔴 Losers: {len(losers)}\n")

    if trending:
        top_mover = trending[0]
        direction = "up" if top_mover["pct_change"] >= 0 else "down"
        lines.append(
            f"Biggest mover: <b>{top_mover['pair']}</b>, {direction} "
            f"{abs(top_mover['pct_change']):.2f}% to {top_mover['rate']:.4f}.\n"
        )

    lines.append("<b>Full board:</b>")
    for item in trending:
        arrow = "🟢" if item["pct_change"] >= 0 else "🔴"
        lines.append(f"{arrow} {item['pair']}: {item['rate']:.4f} ({item['pct_change']:+.2f}%)")

    await query.edit_message_text(
        "\n".join(lines), parse_mode=ParseMode.HTML, reply_markup=BACK_KB
    )
