from core import DEFAULT_FILTERS, getOrCreateChatConfig
from data.database import updateChatConfig


def register(bot):
    @bot.message_handler(commands=["resetfilters"])
    def handle_resetfilters(message):
        chatId = message.chat.id
        chatConfig = getOrCreateChatConfig(chatId)
        chatConfig["filters"] = DEFAULT_FILTERS.copy()
        updateChatConfig(chatId, chatConfig)

        bot.reply_to(message, "✅ Filtros restaurados por defecto y seguimiento reiniciado.")
