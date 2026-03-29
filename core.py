import json
import logging
import os
import threading
import time
from typing import Dict, List, Optional, TypedDict
from datetime import datetime

from telebot import TeleBot
from api import Course, CourseFilters, fetch_courses


DATA_FILE = "bot_state.json"

POLL_INTERVAL_SECONDS = int(os.getenv("POLL_INTERVAL_SECONDS", "2700"))

DEFAULT_FILTERS: CourseFilters = {
    "uni_countries": None,
    "disciplinary_field": None,
    "course_university": None,
    "uni_languages": None,
    "course_levels": None,
    "uni_search": None,
}

ALLOWED_FILTER_KEYS = set(DEFAULT_FILTERS.keys())
LOCK = threading.RLock()

class ConfigChat(TypedDict, total=False):
    filters: CourseFilters
    last_revision: Optional[str]
    isSubcribed: bool


def _default_chatConfig() -> ConfigChat:
    return {
        "filters": DEFAULT_FILTERS.copy(),
        "last_revision": datetime.now().isoformat(),
        "isSubcribed": False,
    }

def load_state() -> Dict[str, ConfigChat]:
    if not os.path.exists(DATA_FILE):
        return {}

    try:
        with open(DATA_FILE, "r", encoding="utf-8") as file:
            state : Dict[str, ConfigChat] = json.load(file)
    except (json.JSONDecodeError, OSError):
        logging.exception("No se pudo leer el estado, se inicia estado limpio")
        return {}

    if not isinstance(state, dict):
        return {}

    return state


def save_state(state: Dict[str, ConfigChat]) -> None:
    temp_file = f"{DATA_FILE}.tmp"

    with open(temp_file, "w", encoding="utf-8") as file:
        json.dump(state, file, ensure_ascii=False, indent=2)
    os.replace(temp_file, DATA_FILE)

STATE = load_state()

def getCoursesWithUserFilters(chat_id: int) -> tuple[CourseFilters, List[Course]]:
    chatConfig = get_or_create_chat(chat_id)
    filters = chatConfig["filters"].copy()
    return filters, fetch_courses(filters)

def get_or_create_chat(chat_id: int) -> ConfigChat:
    chat_key = str(chat_id)
    with LOCK:
        if chat_key not in STATE.keys():
            STATE[chat_key] = _default_chatConfig()
            save_state(STATE)
        return STATE[chat_key]


def update_chat_filter(chat_id: int, filter_key: str, filter_value: Optional[str]) -> ConfigChat:
    if filter_key not in ALLOWED_FILTER_KEYS:
        raise KeyError(filter_key)

    chatConfig = get_or_create_chat(chat_id)
    with LOCK:
        chatConfig["filters"][filter_key] = filter_value
        save_state(STATE)
        return chatConfig

def format_course_message(course: Course) -> str:
    title = course.get("post_title") or "Sin título"
    link = course.get("guid") or "Sin enlace"
    modified = course.get("post_modified") or "Sin fecha"

    return (
        f"<b>{title}</b>\n"
        f"• <b>Actualizado:</b> {modified}\n"
        f"• <b>Enlace:</b> {link}"
    )

def formatCourseFilters(filters: CourseFilters) -> str:
    def formatCourseFilter(key: str) -> str:
        value = filters.get(key)
        return value if value is not None and value != "" else "Sin Valor"

    return (
        f"• <b>País:</b> {formatCourseFilter('uni_countries')}\n"
        f"• <b>Área disciplinaria:</b> {formatCourseFilter('disciplinary_field')}\n"
        f"• <b>Universidad:</b> {formatCourseFilter('course_university')}\n"
        f"• <b>Idioma:</b> {formatCourseFilter('uni_languages')}\n"
        f"• <b>Nivel académico:</b> {formatCourseFilter('course_levels')}\n"
        f"• <b>Palabra clave:</b> {formatCourseFilter('uni_search')}"
    )

def check_for_new_courses(bot, chat_id: int, notify: bool = True, showMessage: bool = False) -> int:
    chatConfig = get_or_create_chat(chat_id)
    last_revision = chatConfig["last_revision"]
    filters = chatConfig["filters"].copy()

    if showMessage:
        bot.send_message(
            chat_id,
            f"Revisando novedades... Posteriores a {last_revision or 'sin fecha'}",
        )

    courses = fetch_courses(filters)

    with LOCK:
        newest_revision = courses[0].get("post_date") if courses else None

        if not last_revision:
            chatConfig["last_revision"] = newest_revision
            save_state(STATE)

            return 0

        new_courses: List[Course] = []
        for course in courses:
            course_date = course.get("post_date")
            if not course_date:
                continue
            if course_date > last_revision:
                new_courses.append(course)
            else:
                break

        if notify:
            for course in new_courses:
                bot.send_message(chat_id, format_course_message(course), disable_web_page_preview=True)

        if newest_revision:
            chatConfig["last_revision"] = newest_revision
        save_state(STATE)
        return len(new_courses)

def monitor_loop(bot: TeleBot) -> None:
    print("Iniciando monitor de cursos...")
    while True:
        time.sleep(POLL_INTERVAL_SECONDS)

        chat_ids = []
        with LOCK:
            for chat_id_str, chatConfig in STATE.items():
                if chatConfig["isSubcribed"]:
                    try:
                        chat_id = int(chat_id_str)
                        chat_ids.append(chat_id)
                    except ValueError:
                        logging.warning("Chat ID inválido en estado: %s", chat_id_str)

        for chat_id in chat_ids:
            try:
                check_for_new_courses(bot, chat_id, notify=True, showMessage=False)
            except Exception:
                logging.exception("Error monitoreando chat %s", chat_id)
