from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

from services import news_api

BACK_KB = InlineKeyboardMarkup([[InlineKeyboardButton("⬅ Back to Menu", callback_data="back_menu")]])


async def show_news(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("📰 Fetching latest Forex news...")

    articles = await news_api.get_forex_news(limit=5)

    if not articles:
        text = (
            "📰 <b>Forex News</b>\n\n"
            "No news available right now. Make sure NEWS_API_KEY is set "
            "in your environment, or try again shortly."
        )
    else:
        lines = ["📰 <b>Latest Forex News</b>\n"]
        for a in articles:
            lines.append(f"• <a href=\"{a['url']}\">{a['title']}</a> — {a['source']}")
        text = "\n".join(lines)

    await query.edit_message_text(
        text, parse_mode=ParseMode.HTML, reply_markup=BACK_KB, disable_web_page_preview=True
    )
