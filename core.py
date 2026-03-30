import logging
import os
import time
from typing import List, Optional

from telebot import TeleBot
from data.api import Course, CourseFilters, fetch_courses
from data.database import getAllChatConfigs, getOrCreateChatConfig, updateChatConfig
from data.types import ChatConfig
from utilsChat import format_course_message


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

def getCoursesWithUserFilters(chat_id: int) -> tuple[CourseFilters, List[Course]]:
    chatConfig = getOrCreateChatConfig(chat_id)
    filters = chatConfig["filters"].copy()
    return filters, fetch_courses(filters)

def update_chat_filter(chat_id: int, filter_key: str, filter_value: Optional[str]) -> ChatConfig:
    if filter_key not in ALLOWED_FILTER_KEYS:
        raise KeyError(filter_key)

    chatConfig = getOrCreateChatConfig(chat_id)
    chatConfig["filters"][filter_key] = filter_value
    return updateChatConfig(chat_id, chatConfig)

def check_for_new_courses(bot, chat_id: int, notify: bool = True, showMessage: bool = False) -> int:
    chatConfig = getOrCreateChatConfig(chat_id)
    last_revision = chatConfig["last_revision"]
    filters = chatConfig["filters"].copy()

    if showMessage:
        bot.send_message(
            chat_id,
            f"Revisando novedades... Posteriores a {last_revision or 'sin fecha'}",
        )

    courses = fetch_courses(filters)

    newest_revision = courses[0].get("post_date") if courses else None

    if not last_revision:
        chatConfig["last_revision"] = newest_revision
        updateChatConfig(chat_id, chatConfig)

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
    updateChatConfig(chat_id, chatConfig)
    return len(new_courses)

def monitor_loop(bot: TeleBot) -> None:
    print("Iniciando monitor de cursos...")
    while True:
        time.sleep(POLL_INTERVAL_SECONDS)

        chat_ids = []
        chatConfigs = getAllChatConfigs()

        for chat_id_str, ChatConfig in chatConfigs.items():
            if ChatConfig["isSubcribed"]:
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
