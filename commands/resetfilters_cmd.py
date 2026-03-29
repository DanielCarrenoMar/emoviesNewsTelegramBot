from core import DEFAULT_FILTERS, LOCK, STATE, get_or_create_chat, save_state


def register(bot):
    @bot.message_handler(commands=["resetfilters"])
    def handle_resetfilters(message):
        chat_state = get_or_create_chat(message.chat.id)
        with LOCK:
            chat_state["filters"] = DEFAULT_FILTERS.copy()
            save_state(STATE)

        bot.reply_to(message, "✅ Filtros restaurados por defecto y seguimiento reiniciado.")
