from dataclasses import dataclass


@dataclass
class CategoryModel:
    category_id: str
    name: str
    color: str = "#888888"
    is_default: bool = False
    mongo_id: str | None = None
