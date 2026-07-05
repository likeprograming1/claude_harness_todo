from enum import StrEnum

DEFAULT_CATEGORY_IDS: frozenset[str] = frozenset(
    {"cat_work", "cat_personal", "cat_urgent", "cat_focus"}
)


class Priority(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
