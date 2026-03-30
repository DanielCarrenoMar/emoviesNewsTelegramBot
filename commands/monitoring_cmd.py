from core import getOrCreateChatConfig
from data.database import updateChatConfig


def register(bot):
    @bot.message_handler(commands=["on"])
    def handle_on(message):
        chatId = message.chat.id
        chatConfig = getOrCreateChatConfig(message.chat.id)

        chatConfig["isSubcribed"] = True
        updateChatConfig(chatId, chatConfig)
        bot.reply_to(message, "✅ Monitoreo automático activado.")

    @bot.message_handler(commands=["off"])
    def handle_off(message):
        chatId = message.chat.id
        chatConfig = getOrCreateChatConfig(message.chat.id)

        chatConfig["isSubcribed"] = False
        updateChatConfig(chatId, chatConfig)
        bot.reply_to(message, "⏸️ Monitoreo automático pausado.")
