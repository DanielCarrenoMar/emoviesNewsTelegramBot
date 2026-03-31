from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup

from core import (
    DEFAULT_FILTERS,
    getOrCreateChatConfig,
    update_chat_filter,
)
from utilsChat import formatCourseFilters

FILTER_LABELS = {
    "uni_countries": "País",
    "disciplinary_field": "Área disciplinaria",
    "course_university": "Universidad",
    "uni_languages": "Idioma",
    "course_levels": "Nivel académico",
    "uni_search": "Palabra clave",
}

FILTER_MENU_ORDER = list(DEFAULT_FILTERS.keys())

FILTER_QUICK_OPTIONS = {
    "uni_countries": [
        ("Argentina", "16"),
        ("Bolivia", "17"),
        ("Brasil", "43"),
        ("Brazil", "197"),
        ("Canada", "6"),
        ("Chile", "18"),
        ("Colombia", "19"),
        ("Ecuador", "20"),
        ("El Salvador", "201"),
        ("Mexico", "21"),
        ("Nicaragua", "199"),
        ("Panamá", "44"),
        ("Paraguay", "194"),
        ("Peru", "22"),
        ("República Dominicana", "45"),
        ("Venezuela", "23"),
    ],
    "course_university": [

    ],
    "uni_languages": [

    ],
    "course_levels": [
        ("Doctorado/Doctorate", "119"),
        ("Formación continua/ Continuous training", "124"),
        ("Posgrado/Postgraduate", "79"),
        ("Pregrado/Undergraduate", "86"),
        ("Técnico-Tecnológico Superior/ Technical-Technological", "112"),
    ],
    "disciplinary_field": [
        ("Administración de empresas", "220"),
        ("Agronomía y estudios de la tierra", "262"),
        ("Arquitectura y diseño", "322"),
        ("Artes", "292"),
        ("Artes gráficas y escénicas", "294"),
        ("Artes plásticas", "296"),
        ("Biología", "326"),
        ("Ciencias administrativas", "218"),
        ("Ciencias Biológicas", "260"),
        ("Ciencias de la comunicación", "284"),
        ("Ciencias de la salud", "238"),
        ("Ciencias económico-administrativas", "208"),
        ("Ciencias exactas y naturales", "324"),
        ("Ciencias politicas", "304"),
        ("Ciencias sociales y Humanidades", "302"),
        ("Comunicación", "288"),
        ("Contabilidad", "222"),
        ("Deportes", "342"),
        ("Derecho", "306"),
        ("Economía", "210"),
        ("Educación", "344"),
        ("Educación y pedagogía", "340"),
        ("Enfermería", "240"),
        ("Farmacia", "242"),
        ("Filosofía y ética", "308"),
        ("Finanzas", "224"),
        ("Física", "328"),
        ("Geografía", "330"),
        ("Geología", "332"),
        ("Gestión empresarial", "226"),
        ("Historia", "310"),
        ("Hotelería y turismo", "228"),
        ("Idiomas", "346"),
        ("Ingeniería Civil", "270"),
        ("Ingeniería de Sistemas", "280"),
        ("Ingeniería Eléctrica", "272"),
        ("Ingeniería Electrónica", "274"),
        ("Ingeniería Industrial", "276"),
        ("Ingeniería Mecánica", "278"),
        ("Ingenierías", "268"),
        ("Literatura", "312"),
        ("Macroeconomía", "212"),
        ("Matemáticas", "334"),
        ("Medicina", "244"),
        ("Mercadotecnia y publicidad", "230"),
        ("Música", "298"),
        ("Negocios Internacionales", "232"),
        ("Nutrición", "246"),
        ("Odontología", "248"),
        ("Otra Arte", "300"),
        ("Otra Ciencia administrativa", "236"),
        ("Otra Ciencia Biológica", "266"),
        ("Otra Ciencia de la comunicación", "290"),
        ("Otra Ciencia de la salud", "258"),
        ("Otra Ciencia económico-administrativa", "216"),
        ("Otra Ciencia exacta o natural", "338"),
        ("Otra Ciencia social o humanidad", "320"),
        ("Otra Educación y pedagogía", "350"),
        ("Otra Ingeniería", "282"),
        ("Pedagogía", "348"),
        ("Periodismo", "286"),
        ("Psicología", "250"),
        ("Química", "336"),
        ("Religión y teología", "314"),
        ("Salud infantil", "254"),
        ("Salud y protección laboral", "252"),
        ("Servicios", "234"),
        ("Sociología", "316"),
        ("Terapia y rehabilitación", "256"),
        ("Trabajo Social", "318"),
        ("Veterinaria y zootecnia", "264"),
    ],

}


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
        InlineKeyboardButton("Cualquiera", callback_data=f"menu:set:{filter_key}:"),
        InlineKeyboardButton("Escribir valor", callback_data=f"menu:custom:{filter_key}"),
    )
    keyboard.add(InlineKeyboardButton("Volver", callback_data="menu:back"))
    return keyboard


def register(bot):
    def _render_menu(chat_id: int) -> str:
        chat_state = getOrCreateChatConfig(chat_id)
        return "<b>Filtros Configurados</b>\n\n" + formatCourseFilters(chat_state["filters"])

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
