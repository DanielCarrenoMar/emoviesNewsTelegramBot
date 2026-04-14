from datetime import datetime

from data.types import CourseAPI, CourseFilters

def _courseDateStr(course: CourseAPI) -> str:
    dates: list[datetime] = []
    
    for key in ("post_modified", "post_date"):
        raw_date = course.get(key)
        if raw_date:
            try:
                dates.append(datetime.fromisoformat(raw_date))
            except ValueError:
                pass
                
    return max(dates).strftime("%Y-%m-%d %H:%M:%S") if dates else datetime.min.strftime("%Y-%m-%d %H:%M:%S")

def formatCourseMessage(course: CourseAPI) -> str:
    title = course.get("post_title") or "Sin título"
    link = f"https://emovies.oui-iohe.org/nuestros-cursos/{course.get('post_name')}" or course.get("guid")
    modified = _courseDateStr(course)

    return (
        f"<b>{title}</b>\n"
        f"• <b>Actualizado:</b> {modified}\n"
        f"• <b>Enlace:</b>  {link}"
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