from dataclasses import dataclass
from datetime import date, datetime
from typing import Optional, TypedDict

class CourseFilters(TypedDict, total=False):
    uni_countries: Optional[str]
    disciplinary_field: Optional[str]
    course_university: Optional[str]
    uni_languages: Optional[str]
    course_levels: Optional[str]
    uni_search: Optional[str]

class CourseAPI(TypedDict, total=False):
    ID: int
    post_author: str
    post_date: str
    post_date_gmt: str
    post_content: str
    post_title: str
    post_excerpt: str
    post_status: str
    comment_status: str
    ping_status: str
    post_password: str
    post_name: str
    to_ping: str
    pinged: str
    post_modified: str
    post_modified_gmt: str
    post_content_filtered: str
    post_parent: int
    guid: str
    menu_order: int
    post_type: str
    post_mime_type: str
    comment_count: str
    filter: str

@dataclass(slots=True)
class Course:
    id: int
    title: str
    link: str
    date: date

def _parse_api_datetime(value: Optional[str]) -> Optional[date]:
    if not value:
        return None

    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).date()
    except ValueError:
        return None

def courseFromAPI(course_api: CourseAPI) -> Optional[Course]:
    try:
        courseDate = _parse_api_datetime(course_api.get("post_date"))
        courseModifiedDate = _parse_api_datetime(course_api.get("post_modified"))

        if courseDate is None and courseModifiedDate is None:
            raise ValueError("No hay fechas válidas en el curso")

        courseSlug = course_api.get("post_name", "")
        courseLink = f"https://emovies.oui-iohe.org/nuestros-cursos/{courseSlug}"

        if not courseSlug:
            courseLink = course_api.get("guid", "")

        return Course(
            id=course_api["ID"],
            title=course_api.get("post_title", "Sin título"),
            link=courseLink,
            date=max(
                parsed_date
                for parsed_date in (courseDate, courseModifiedDate)
                if parsed_date is not None
            ),
        )
    except (KeyError, ValueError) as e:
        print(f"Error al convertir curso API a curso: {course_api}")
        raise e


class ChatConfig(TypedDict, total=False):
    filters: CourseFilters
    lastRevision: str
    isSubcribed: bool