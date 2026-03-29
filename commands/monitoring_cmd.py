from core import LOCK, STATE, get_or_create_chat, save_state


def register(bot):
    @bot.message_handler(commands=["on"])
    def handle_on(message):
        chat_state = get_or_create_chat(message.chat.id)
        with LOCK:
            chat_state["isSubcribed"] = True
            save_state(STATE)
        bot.reply_to(message, "✅ Monitoreo automático activado.")

    @bot.message_handler(commands=["off"])
    def handle_off(message):
        chat_state = get_or_create_chat(message.chat.id)
        with LOCK:
            chat_state["isSubcribed"] = False
            save_state(STATE)
        bot.reply_to(message, "⏸️ Monitoreo automático pausado.")
