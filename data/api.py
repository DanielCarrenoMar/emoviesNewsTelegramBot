from datetime import datetime

import requests
from typing import Any, Dict, List, Optional, TypedDict

from data.types import CourseAPI, CourseFilters

REQUEST_TIMEOUT_SECONDS = 30
API_URL = "https://emovies.oui-iohe.org/wp-admin/admin-ajax.php"


class CoursesPayload(TypedDict, total=False):
    max_num_pages: int
    post_count: int
    posts: List[CourseAPI]


def _course_date(course: CourseAPI) -> datetime:
    dates = []
    
    for key in ("post_modified", "post_date"):
        raw_date = course.get(key)
        if raw_date:
            try:
                dates.append(datetime.fromisoformat(raw_date))
            except ValueError:
                pass
                
    return max(dates) if dates else datetime.min

def filtersNoneToNaN(filters: CourseFilters) -> CourseFilters:
    return {k: (v if v is not None else "NaN") for k, v in filters.items()}

def fetch_courses(filters: CourseFilters) -> List[CourseAPI]:
    def _fetch_page(page: int) -> CoursesPayload:
        validFilters = filtersNoneToNaN(filters)
        validFilters["uni_search"] = "" if filters.get("uni_search") is None else filters["uni_search"]
        params = {"action": "get_courses", **validFilters, "page": str(page)}

        response = requests.get(API_URL, params=params, timeout=REQUEST_TIMEOUT_SECONDS)
        response.raise_for_status()

        payload = response.json()
        if not payload.get("success"):
            raise ValueError("La API respondió success=false")
        courses_payload : CoursesPayload = payload.get("data", {}).get("courses", {})
        
        if not isinstance(courses_payload, dict):
            raise ValueError("La API devolvió un formato inesperado para courses")
        print(f"Fetched page {page} with {courses_payload.get('post_count', 0)} courses")
        return courses_payload
    
    first_payload = _fetch_page(1)

    max_num_pages = first_payload.get("max_num_pages", 1)
    courses_by_id: Dict[int, CourseAPI] = {}

    for course in first_payload.get("posts", []):
        if isinstance(course, dict) and course.get("ID") is not None:
            courses_by_id[int(course["ID"])] = course

    for page in range(2, max_num_pages + 1):
        payload = _fetch_page(page)
        for course in payload.get("posts", []):
            if isinstance(course, dict) and course.get("ID") is not None:
                courses_by_id[int(course["ID"])] = course

    return sorted(courses_by_id.values(), key=_course_date, reverse=True)
