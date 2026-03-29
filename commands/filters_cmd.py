from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup

from core import (
    FILTER_LABELS,
    FILTER_MENU_ORDER,
    FILTER_QUICK_OPTIONS,
    formatCourseFilters,
    get_or_create_chat,
    update_chat_filter,
)


def _build_menu_keyboard() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(row_width=2)

    buttons = [
        InlineKeyboardButton(FILTER_LABELS.get(filter_key, filter_key), callback_data=f"menu:filter:{filter_key}")
        for filter_key in FILTER_MENU_ORDER
    ]
    keyboard.add(*buttons)
    keyboard.add(
        InlineKeyboardButton("Restablecer filtros", callback_data="menu:reset"),
        InlineKeyboardButton("Cerrar", callback_data="menu:close"),
    )
    return keyboard


def _build_value_keyboard(filter_key: str) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(row_width=2)

    for label, value in FILTER_QUICK_OPTIONS.get(filter_key, []):
        keyboard.add(InlineKeyboardButton(label, callback_data=f"menu:set:{filter_key}:{value}"))

    keyboard.add(
        InlineKeyboardButton("Sin valor", callback_data=f"menu:set:{filter_key}:"),
        InlineKeyboardButton("Escribir valor", callback_data=f"menu:custom:{filter_key}"),
    )
    keyboard.add(InlineKeyboardButton("Volver", callback_data="menu:back"))
    return keyboard


def register(bot):
    def _render_menu(chat_id: int) -> str:
        chat_state = get_or_create_chat(chat_id)
        return "<b>Menú de filtros</b>\n\n" + formatCourseFilters(chat_state["filters"])

    def _ask_for_custom_value(message, filter_key: str) -> None:
        filter_label = FILTER_LABELS.get(filter_key, filter_key)
        if filter_key == "uni_search":
            prompt = f"Escribe la palabra clave para <b>{filter_label}</b>."
        else:
            prompt = f"Escribe el valor para <b>{filter_label}</b> o envía <b>Sin valor</b> para limpiarlo."

        sent_message = bot.send_message(message.chat.id, prompt)
        bot.register_next_step_handler(sent_message, _handle_custom_value, filter_key)

    def _handle_custom_value(message, filter_key: str) -> None:
        raw_value = (message.text or "").strip()
        if not raw_value or raw_value.lower() in {"sin valor", "none", "null"}:
            value = None
        else:
            value = raw_value

        update_chat_filter(message.chat.id, filter_key, value)
        bot.send_message(
            message.chat.id,
            _render_menu(message.chat.id),
            reply_markup=_build_menu_keyboard(),
        )

    @bot.message_handler(commands=["filters"])
    def handle_filters(message):
        bot.send_message(
            message.chat.id,
            _render_menu(message.chat.id),
            reply_markup=_build_menu_keyboard(),
        )

    @bot.callback_query_handler(func=lambda call: bool(call.data and call.data.startswith("menu:")))
    def handle_menu_callback(call):
        chat_id = call.message.chat.id
        data = call.data or ""

        if data == "menu:close":
            bot.answer_callback_query(call.id)
            bot.edit_message_reply_markup(chat_id, call.message.message_id, reply_markup=None)
            return

        if data == "menu:back":
            bot.answer_callback_query(call.id)
            bot.edit_message_text(
                _render_menu(chat_id),
                chat_id,
                call.message.message_id,
                reply_markup=_build_menu_keyboard(),
            )
            return

        if data == "menu:reset":
            update_chat_filter(chat_id, "uni_countries", None)
            update_chat_filter(chat_id, "disciplinary_field", None)
            update_chat_filter(chat_id, "course_university", None)
            update_chat_filter(chat_id, "uni_languages", None)
            update_chat_filter(chat_id, "course_levels", None)
            update_chat_filter(chat_id, "course_drafts", None)
            update_chat_filter(chat_id, "uni_search", None)
            bot.answer_callback_query(call.id, "Filtros restaurados")
            bot.edit_message_text(
                _render_menu(chat_id),
                chat_id,
                call.message.message_id,
                reply_markup=_build_menu_keyboard(),
            )
            return

        if data.startswith("menu:filter:"):
            filter_key = data.split(":", 2)[2]
            bot.answer_callback_query(call.id)

            if filter_key == "uni_search" or filter_key not in FILTER_QUICK_OPTIONS:
                _ask_for_custom_value(call.message, filter_key)
                return

            bot.edit_message_text(
                f"<b>{FILTER_LABELS.get(filter_key, filter_key)}</b>\nSelecciona un valor.",
                chat_id,
                call.message.message_id,
                reply_markup=_build_value_keyboard(filter_key),
            )
            return

        if data.startswith("menu:custom:"):
            filter_key = data.split(":", 2)[2]
            bot.answer_callback_query(call.id)
            _ask_for_custom_value(call.message, filter_key)
            return

        if data.startswith("menu:set:"):
            _, _, filter_key, raw_value = data.split(":", 3)
            value = raw_value or None
            update_chat_filter(chat_id, filter_key, value)
            bot.answer_callback_query(call.id, "Filtro actualizado")
            bot.edit_message_text(
                _render_menu(chat_id),
                chat_id,
                call.message.message_id,
                reply_markup=_build_menu_keyboard(),
            )
