"""
Background jobs:
 - daily_update: broadcasts a market summary to every registered user
 - check_alerts: polls live rates and notifies users whose price alerts triggered
"""
import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from telegram.constants import ParseMode
from telegram.error import Forbidden, BadRequest

import config
import database as db
from services import forex_api

logger = logging.getLogger(__name__)


async def _build_daily_summary_text() -> str:
    trending = await forex_api.get_trending(config.MAJOR_PAIRS)
    lines = ["📅 <b>Daily Forex Update</b>\n"]
    for item in trending:
        arrow = "🟢" if item["pct_change"] >= 0 else "🔴"
        lines.append(
            f"{arrow} {item['pair']}: {item['rate']:.4f} ({item['pct_change']:+.2f}%)"
        )
    lines.append("\nSent automatically by ForexTrend AI ⏰")
    return "\n".join(lines)


async def daily_update_job(application):
    text = await _build_daily_summary_text()
    user_ids = db.get_all_user_ids()
    for uid in user_ids:
        try:
            await application.bot.send_message(uid, text, parse_mode=ParseMode.HTML)
        except (Forbidden, BadRequest):
            continue
        except Exception as e:
            logger.warning("Failed to send daily update to %s: %s", uid, e)


async def check_alerts_job(application):
    alerts = db.get_all_active_alerts()
    if not alerts:
        return

    pairs = list({a["pair"] for a in alerts})
    rates = await forex_api.get_rates(pairs)

    for alert in alerts:
        rate = rates.get(alert["pair"])
        if rate is None:
            continue
        triggered = (
            (alert["direction"] == "above" and rate >= alert["target_price"]) or
            (alert["direction"] == "below" and rate <= alert["target_price"])
        )
        if triggered:
            try:
                await application.bot.send_message(
                    alert["user_id"],
                    f"🔔 <b>Price Alert Triggered</b>\n"
                    f"{alert['pair']} is now {rate:.4f} "
                    f"({alert['direction']} your target {alert['target_price']:.4f})",
                    parse_mode=ParseMode.HTML,
                )
            except (Forbidden, BadRequest):
                pass
            except Exception as e:
                logger.warning("Failed to notify alert to %s: %s", alert["user_id"], e)
            db.deactivate_alert(alert["id"])


def setup_scheduler(application) -> AsyncIOScheduler:
    scheduler = AsyncIOScheduler(timezone="UTC")

    scheduler.add_job(
        daily_update_job,
        trigger=CronTrigger(hour=config.DAILY_UPDATE_HOUR, minute=config.DAILY_UPDATE_MINUTE),
        args=[application],
        id="daily_update",
        replace_existing=True,
    )

    scheduler.add_job(
        check_alerts_job,
        trigger="interval",
        minutes=config.ALERT_CHECK_INTERVAL_MINUTES,
        args=[application],
        id="check_alerts",
        replace_existing=True,
    )

    scheduler.start()
    return scheduler
