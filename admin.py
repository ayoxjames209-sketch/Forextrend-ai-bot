from telegram import Update
from telegram.constants import ParseMode
from telegram.error import Forbidden, BadRequest
from telegram.ext import ContextTypes

import config
import database as db


def _is_admin(user_id: int) -> bool:
    return user_id in config.ADMIN_IDS


async def broadcast_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not _is_admin(user_id):
        await update.message.reply_text("⛔ This command is admin-only.")
        return

    if not context.args:
        await update.message.reply_text("Usage: /broadcast <message>")
        return

    message = " ".join(context.args)
    user_ids = db.get_all_user_ids()

    sent, failed = 0, 0
    for uid in user_ids:
        try:
            await context.bot.send_message(uid, f"📢 {message}", parse_mode=ParseMode.HTML)
            sent += 1
        except (Forbidden, BadRequest):
            failed += 1

    await update.message.reply_text(f"Broadcast sent: {sent} delivered, {failed} failed.")


async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not _is_admin(user_id):
        await update.message.reply_text("⛔ This command is admin-only.")
        return

    total_users = db.get_user_count()
    await update.message.reply_text(f"📊 Bot stats\nTotal users: {total_users}")
