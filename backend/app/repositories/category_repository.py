import dataclasses
from typing import Any

from pymongo.errors import DuplicateKeyError

from app.core.exceptions import DuplicateEntityError
from app.core.types import DEFAULT_CATEGORY_IDS
from app.models.category import CategoryModel
from app.repositories.base import BaseRepository, _id_to_str

_DEFAULT_CATEGORIES: list[dict[str, Any]] = [
    {"category_id": "cat_work",     "name": "업무", "color": "#4A6FFF", "is_default": True},
    {"category_id": "cat_personal", "name": "개인", "color": "#FF6B6B", "is_default": True},
    {"category_id": "cat_urgent",   "name": "긴급", "color": "#FF9500", "is_default": True},
    {"category_id": "cat_focus",    "name": "집중", "color": "#34C759", "is_default": True},
]


class CategoryRepository(BaseRepository[CategoryModel]):
    collection_name = "categories"

    def _doc_to_model(self, doc: dict[str, Any]) -> CategoryModel:
        return CategoryModel(
            category_id=str(doc["category_id"]),
            name=str(doc["name"]),
            color=str(doc["color"]),
            is_default=bool(doc.get("is_default", False)),
            mongo_id=_id_to_str(doc["_id"]),
        )

    @staticmethod
    def _model_to_doc(model: CategoryModel) -> dict[str, Any]:
        d = dataclasses.asdict(model)
        d.pop("mongo_id", None)
        return d

    # ── queries ──────────────────────────────────────────────────────────────

    async def list_all(self) -> list[CategoryModel]:
        cursor = self._col().find({}).sort("is_default", -1)
        return [self._doc_to_model(doc) async for doc in cursor]

    async def get_by_id(self, category_id: str) -> CategoryModel | None:
        doc = await self._col().find_one({"category_id": category_id})
        return self._doc_to_model(doc) if doc else None

    async def exists(self, category_id: str) -> bool:
        return await self._col().count_documents({"category_id": category_id}) > 0

    async def is_default(self, category_id: str) -> bool:
        return category_id in DEFAULT_CATEGORY_IDS

    # ── writes ────────────────────────────────────────────────────────────────

    async def create(self, data: dict[str, Any]) -> CategoryModel:
        import uuid
        category_id = str(data.get("category_id") or f"cat_{uuid.uuid4().hex[:6]}")
        model = CategoryModel(
            category_id=category_id,
            name=str(data["name"]),
            color=str(data.get("color", "#888888")),
            is_default=False,
        )
        doc = self._model_to_doc(model)
        try:
            result = await self._col().insert_one(doc)
        except DuplicateKeyError as exc:
            field = "name" if "name" in str(exc) else "category_id"
            value = model.name if field == "name" else category_id
            raise DuplicateEntityError("Category", field, value) from None
        doc["_id"] = result.inserted_id
        return self._doc_to_model(doc)

    async def delete(self, category_id: str) -> bool:
        result = await self._col().delete_one({"category_id": category_id})
        return result.deleted_count > 0

    async def seed_defaults(self) -> None:
        """Insert default categories that are not yet present (idempotent)."""
        for cat in _DEFAULT_CATEGORIES:
            existing = await self._col().find_one({"category_id": cat["category_id"]})
            if existing is None:
                await self._col().insert_one(cat.copy())
