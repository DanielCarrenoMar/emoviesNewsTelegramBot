from typing import Optional, TypedDict


class CourseFilters(TypedDict, total=False):
    uni_countries: Optional[str]
    disciplinary_field: Optional[str]
    course_university: Optional[str]
    uni_languages: Optional[str]
    course_levels: Optional[str]
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


class ChatConfig(TypedDict, total=False):
    filters: CourseFilters
    lastRevision: str
    isSubcribed: bool