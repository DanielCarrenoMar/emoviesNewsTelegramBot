import logging
import os
import threading

from dotenv import load_dotenv 
import telebot
from commands import register_handlers
from core import monitor_loop


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
    )

    load_dotenv()

    token = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
    if not token:
        raise RuntimeError("Falta variable de entorno TELEGRAM_BOT_TOKEN")

    bot = telebot.TeleBot(token, parse_mode="HTML")
    register_handlers(bot)

    monitor_thread = threading.Thread(target=monitor_loop, args=(bot,), daemon=True)
    monitor_thread.start()

    bot.infinity_polling(skip_pending=True, timeout=60, long_polling_timeout=30)