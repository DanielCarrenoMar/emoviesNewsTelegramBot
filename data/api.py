import requests
from typing import Any, Dict, List, Optional, TypedDict

from data.types import Course, CourseFilters

REQUEST_TIMEOUT_SECONDS = 30
API_URL = "https://emovies.oui-iohe.org/wp-admin/admin-ajax.php"


class CoursesPayload(TypedDict, total=False):
    max_num_pages: int
    posts: List[Course]

def filtersNoneToNaN(filters: CourseFilters) -> CourseFilters:
    return {k: (v if v is not None else "NaN") for k, v in filters.items()}

def fetch_courses(filters: CourseFilters) -> List[Course]:
    def _fetch_page(page: int) -> CoursesPayload:
        validFilters = filtersNoneToNaN(filters)
        validFilters["uni_search"] = "" if filters.get("uni_search") is None else filters["uni_search"]
        params = {"action": "get_courses", **validFilters, "page": str(page)}

        url = API_URL + "?" + "&".join(f"{k}={v}" for k, v in params.items())
        print(f"Fetching courses with URL: {url}")

        response = requests.get(API_URL, params=params, timeout=REQUEST_TIMEOUT_SECONDS)
        response.raise_for_status()

        payload = response.json()
        if not payload.get("success"):
            raise ValueError("La API respondió success=false")
        courses_payload : CoursesPayload = payload.get("data", {}).get("courses", {})

        print(f"Fetched page {page} with {len(courses_payload.get('posts', []))} courses")
        
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