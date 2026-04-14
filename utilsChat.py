from data.types import Course, CourseFilters

def formatCourseMessage(course: Course) -> str:
    return (
        f"<b>{course.title}</b>\n"
        f"• <b>Actualizado:</b> {course.date.strftime('%Y-%m-%d %H:%M:%S')}\n"
        f"• <b>Enlace:</b>  {course.link}"
    )

def formatCourseFiltersMessage(filters: CourseFilters) -> str:
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