import logging

from telegram.ext import Application, CommandHandler, CallbackQueryHandler

import config
import database as db
from services.scheduler import setup_scheduler

from handlers.start import start_command, show_main_menu
from handlers.news import show_news
from handlers.trends import show_trends
from handlers.rates import show_rates_menu, show_single_rate
from handlers.analysis import show_analysis
from handlers.econ_calendar import show_calendar
from handlers.alerts import show_alerts_menu, list_alerts, build_alert_conversation_handler
from handlers.favorites import show_favorites, add_favorite, remove_favorite
from handlers.profile import show_profile
from handlers.admin import broadcast_command, stats_command

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


def build_application() -> Application:
    application = Application.builder().token(config.BOT_TOKEN).build()

    # Core
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CallbackQueryHandler(show_main_menu, pattern="^back_menu$"))

    # Menu sections
    application.add_handler(CallbackQueryHandler(show_news, pattern="^menu_news$"))
    application.add_handler(CallbackQueryHandler(show_trends, pattern="^menu_trends$"))
    application.add_handler(CallbackQueryHandler(show_analysis, pattern="^menu_analysis$"))
    application.add_handler(CallbackQueryHandler(show_calendar, pattern="^menu_calendar$"))
    application.add_handler(CallbackQueryHandler(show_profile, pattern="^menu_profile$"))

    # Rates
    application.add_handler(CallbackQueryHandler(show_rates_menu, pattern="^menu_rates$"))
    application.add_handler(CallbackQueryHandler(show_single_rate, pattern="^rate_"))

    # Favorites
    application.add_handler(CallbackQueryHandler(show_favorites, pattern="^menu_favorites$"))
    application.add_handler(CallbackQueryHandler(add_favorite, pattern="^fav_add_"))
    application.add_handler(CallbackQueryHandler(remove_favorite, pattern="^fav_del_"))

    # Alerts (menu + add-alert conversation)
    application.add_handler(CallbackQueryHandler(show_alerts_menu, pattern="^menu_alerts$"))
    application.add_handler(CallbackQueryHandler(list_alerts, pattern="^alert_list$"))
    application.add_handler(build_alert_conversation_handler())

    # Admin
    application.add_handler(CommandHandler("broadcast", broadcast_command))
    application.add_handler(CommandHandler("stats", stats_command))

    return application


def main():
    db.init_db()
    application = build_application()
    setup_scheduler(application)

    logger.info("ForexTrend AI starting (polling mode)...")
    application.run_polling(allowed_updates=["message", "callback_query"])


if __name__ == "__main__":
    main()
