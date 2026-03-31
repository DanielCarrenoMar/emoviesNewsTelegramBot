

from telebot import TeleBot

from core import format_course_message, getCoursesWithUserFilters
from utilsChat import formatCourseFilters


def courseList(bot: TeleBot):
    @bot.message_handler(commands=["courseList"])
    def handle_check(message):
        loadingMessage = bot.send_message(message.chat.id, "⏳ Cargando lista de cursos...")

        filters, courses = getCoursesWithUserFilters(message.chat.id)

        bot.send_message(message.chat.id, formatCourseFilters(filters))

        if not courses:
            bot.reply_to(message, "No se pudieron obtener los cursos en este momento.")
            return
        
        if len(courses) == 0:
            bot.reply_to(message, "No se encontraron cursos con los filtros actuales.")
            return
        
        bot.delete_message(message.chat.id, loadingMessage.message_id)
        bot.send_message(message.chat.id, "📚 <b>Lista de Cursos Actuales:</b>")

        for course in courses:
            response = format_course_message(course) + "\n\n"
            bot.send_message(message.chat.id, response)

