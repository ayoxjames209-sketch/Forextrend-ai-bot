from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.constants import ParseMode
from telegram.ext import ContextTypes, ConversationHandler, MessageHandler, filters, CommandHandler

import config
import database as db

CHOOSING_PAIR, CHOOSING_DIRECTION, ENTERING_PRICE = range(3)

BACK_KB = InlineKeyboardMarkup([[InlineKeyboardButton("⬅ Back to Menu", callback_data="back_menu")]])


def alerts_menu_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("➕ Add Alert", callback_data="alert_add")],
        [InlineKeyboardButton("📋 My Alerts", callback_data="alert_list")],
        [InlineKeyboardButton("⬅ Back to Menu", callback_data="back_menu")],
    ])


async def show_alerts_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        "🔔 <b>Price Alerts</b>\nGet notified when a pair hits your target price.",
        parse_mode=ParseMode.HTML,
        reply_markup=alerts_menu_kb(),
    )


async def list_alerts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    alerts = db.get_user_alerts(user_id)

    if not alerts:
        text = "📋 You have no active alerts yet."
    else:
        lines = ["📋 <b>Your Active Alerts</b>\n"]
        for a in alerts:
            lines.append(f"#{a['id']} — {a['pair']} {a['direction']} {a['target_price']:.4f}")
        text = "\n".join(lines)

    await query.edit_message_text(
        text, parse_mode=ParseMode.HTML,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("⬅ Back", callback_data="menu_alerts")]
        ]),
    )


# ---------- Conversation: Add Alert ----------

def pair_choice_kb() -> InlineKeyboardMarkup:
    rows, row = [], []
    for pair in config.MAJOR_PAIRS:
        row.append(InlineKeyboardButton(pair, callback_data=f"alertpair_{pair}"))
        if len(row) == 2:
            rows.append(row)
            row = []
    if row:
        rows.append(row)
    rows.append([InlineKeyboardButton("❌ Cancel", callback_data="alert_cancel")])
    return InlineKeyboardMarkup(rows)


async def add_alert_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        "Which pair would you like an alert for?", reply_markup=pair_choice_kb()
    )
    return CHOOSING_PAIR


async def pair_chosen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    pair = query.data.replace("alertpair_", "")
    context.user_data["alert_pair"] = pair

    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("📈 Above", callback_data="dir_above"),
         InlineKeyboardButton("📉 Below", callback_data="dir_below")],
        [InlineKeyboardButton("❌ Cancel", callback_data="alert_cancel")],
    ])
    await query.edit_message_text(
        f"Alert for <b>{pair}</b>. Notify me when the price goes:",
        parse_mode=ParseMode.HTML, reply_markup=kb,
    )
    return CHOOSING_DIRECTION


async def direction_chosen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    direction = "above" if query.data == "dir_above" else "below"
    context.user_data["alert_direction"] = direction

    await query.edit_message_text(
        f"Send me the target price for {context.user_data['alert_pair']} "
        f"(e.g. 1.0950). Send /cancel to stop."
    )
    return ENTERING_PRICE


async def price_entered(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    try:
        price = float(text)
    except ValueError:
        await update.message.reply_text("That doesn't look like a number. Try again, e.g. 1.0950")
        return ENTERING_PRICE

    pair = context.user_data["alert_pair"]
    direction = context.user_data["alert_direction"]
    user_id = update.effective_user.id

    db.add_alert(user_id, pair, price, direction)

    await update.message.reply_text(
        f"✅ Alert set: {pair} {direction} {price:.4f}. I'll message you when it triggers."
    )
    context.user_data.pop("alert_pair", None)
    context.user_data.pop("alert_direction", None)
    return ConversationHandler.END


async def alert_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query:
        await query.answer()
        await query.edit_message_text("Alert setup cancelled.", reply_markup=alerts_menu_kb())
    else:
        await update.message.reply_text("Alert setup cancelled.")
    context.user_data.pop("alert_pair", None)
    context.user_data.pop("alert_direction", None)
    return ConversationHandler.END


def build_alert_conversation_handler():
    from telegram.ext import CallbackQueryHandler
    return ConversationHandler(
        entry_points=[CallbackQueryHandler(add_alert_start, pattern="^alert_add$")],
        states={
            CHOOSING_PAIR: [CallbackQueryHandler(pair_chosen, pattern="^alertpair_")],
            CHOOSING_DIRECTION: [CallbackQueryHandler(direction_chosen, pattern="^dir_")],
            ENTERING_PRICE: [MessageHandler(filters.TEXT & ~filters.COMMAND, price_entered)],
        },
        fallbacks=[
            CallbackQueryHandler(alert_cancel, pattern="^alert_cancel$"),
            CommandHandler("cancel", alert_cancel),
        ],
        per_message=False,
    )
