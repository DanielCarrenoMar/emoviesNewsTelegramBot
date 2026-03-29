from core import get_or_create_chat, fetch_courses, DEFAULT_FILTERS


def register(bot):
    @bot.message_handler(commands=["start"])
    def handle_start(message):
        get_or_create_chat(message.chat.id)
        bot.reply_to(
            message,
            "👋 Hola. Usa /filters para configurar filtros o /help para ver todos los comandos.",
        )
       
