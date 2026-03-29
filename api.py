import requests
from typing import Any, Dict, List, Optional, TypedDict

REQUEST_TIMEOUT_SECONDS = 30
API_URL = "https://emovies.oui-iohe.org/wp-admin/admin-ajax.php"

class CourseFilters(TypedDict, total=False):
    uni_countries: Optional[str]
    disciplinary_field: Optional[str]
    course_university: Optional[str]
    uni_languages: Optional[str]
    course_levels: Optional[str]
    course_drafts: Optional[str]
    uni_search: Optional[str]

class Course(TypedDict, total=False):
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


class CoursesPayload(TypedDict, total=False):
    max_num_pages: int
    posts: List[Course]

def filtersNoneToNaN(filters: CourseFilters) -> CourseFilters:
    return {k: (v if v is not None else "NaN") for k, v in filters.items()}

def fetch_courses(filters: CourseFilters) -> List[Course]:
    def _fetch_page(page: int) -> CoursesPayload:
        params = {"action": "get_courses", **filtersNoneToNaN(filters), "page": str(page)}
        response = requests.get(API_URL, params=params, timeout=REQUEST_TIMEOUT_SECONDS)
        response.raise_for_status()

        payload = response.json()
        if not payload.get("success"):
            raise ValueError("La API respondió success=false")
        courses_payload = payload.get("data", {}).get("courses", {})
        if not isinstance(courses_payload, dict):
            raise ValueError("La API devolvió un formato inesperado para courses")
        return courses_payload
    
    first_payload = _fetch_page(1)

    max_num_pages = first_payload.get("max_num_pages", 1)
    courses_by_id: Dict[int, Course] = {}

    for course in first_payload.get("posts", []):
        if isinstance(course, dict) and course.get("ID") is not None:
            courses_by_id[int(course["ID"])] = course

    for page in range(2, max_num_pages + 1):
        payload = _fetch_page(page)
        for course in payload.get("posts", []):
            if isinstance(course, dict) and course.get("ID") is not None:
                courses_by_id[int(course["ID"])] = course

    return sorted(courses_by_id.values(), key=lambda x: x.get("post_date", ""), reverse=True)