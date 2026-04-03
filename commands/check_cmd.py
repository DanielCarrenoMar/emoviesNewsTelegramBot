import logging

from core import check_for_new_courses


def register(bot):
    @bot.message_handler(commands=["check"])
    def handle_check(message):
        chat_id = message.chat.id
        print(f"/check ejecutado para chat_id {chat_id}")
        try:
            count = check_for_new_courses(bot, chat_id, notify=True, showMessage=True)
            if count == 0:
                bot.reply_to(message, "Sin cursos nuevos por ahora.")
        except Exception as error:
            logging.exception("Error en /check")
            bot.reply_to(message, f"❌ Error consultando la API: {error}")
