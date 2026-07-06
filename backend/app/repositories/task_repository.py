import dataclasses
import uuid
from datetime import datetime
from typing import Any

from pymongo import ReturnDocument
from pymongo.errors import DuplicateKeyError

from app.core.exceptions import DuplicateEntityError
from app.core.types import Priority
from app.models.task import TaskModel
from app.repositories.base import BaseRepository, _id_to_str


class TaskRepository(BaseRepository[TaskModel]):
    collection_name = "tasks"

    def _doc_to_model(self, doc: dict[str, Any]) -> TaskModel:
        return TaskModel(
            task_id=str(doc["task_id"]),
            title=str(doc["title"]),
            priority=Priority(doc["priority"]),
            is_done=bool(doc["is_done"]),
            due_date=str(doc["due_date"]) if doc.get("due_date") else None,
            due_time=str(doc["due_time"]) if doc.get("due_time") else None,
            category_id=str(doc["category_id"]) if doc.get("category_id") else None,
            notes=str(doc["notes"]) if doc.get("notes") else None,
            completed_at=doc.get("completed_at"),
            created_at=doc["created_at"],
            mongo_id=_id_to_str(doc["_id"]),
        )

    @staticmethod
    def _model_to_doc(model: TaskModel) -> dict[str, Any]:
        d = dataclasses.asdict(model)
        d.pop("mongo_id", None)
        return d

    # ── queries ──────────────────────────────────────────────────────────────

    async def get_by_id(self, task_id: str) -> TaskModel | None:
        doc = await self._col().find_one({"task_id": task_id})
        return self._doc_to_model(doc) if doc else None

    async def list_all(
        self,
        *,
        date: str | None = None,
        category_id: str | None = None,
        is_done: bool | None = None,
        priority: Priority | None = None,
    ) -> list[TaskModel]:
        query: dict[str, Any] = {}
        if date is not None:
            query["due_date"] = date
        if category_id is not None:
            query["category_id"] = category_id
        if is_done is not None:
            query["is_done"] = is_done
        if priority is not None:
            query["priority"] = priority.value
        cursor = self._col().find(query).sort("due_date", 1)
        return [self._doc_to_model(doc) async for doc in cursor]

    async def get_by_due_date_range(
        self, start_date: str, end_date: str
    ) -> list[TaskModel]:
        """Return tasks whose due_date falls within [start_date, end_date]."""
        cursor = self._col().find(
            {"due_date": {"$gte": start_date, "$lte": end_date}}
        )
        return [self._doc_to_model(doc) async for doc in cursor]

    async def count_total_completed(self) -> int:
        return await self._col().count_documents({"is_done": True})

    async def get_completed_with_time(self) -> list[TaskModel]:
        """Return completed tasks that have completed_at set — for insights."""
        cursor = self._col().find({"is_done": True, "completed_at": {"$ne": None}})
        return [self._doc_to_model(doc) async for doc in cursor]

    # ── writes ────────────────────────────────────────────────────────────────

    async def create(self, data: dict[str, Any]) -> TaskModel:
        task_id = str(data.get("task_id") or uuid.uuid4().hex[:8])
        model = TaskModel(
            task_id=task_id,
            title=str(data["title"]),
            priority=Priority(data.get("priority", Priority.MEDIUM)),
            is_done=False,
            due_date=data.get("due_date"),
            due_time=data.get("due_time"),
            category_id=data.get("category_id"),
            notes=data.get("notes"),
            created_at=datetime.utcnow(),
        )
        doc = self._model_to_doc(model)
        try:
            result = await self._col().insert_one(doc)
        except DuplicateKeyError:
            raise DuplicateEntityError("Task", "task_id", task_id) from None
        doc["_id"] = result.inserted_id
        return self._doc_to_model(doc)

    async def update(self, task_id: str, data: dict[str, Any]) -> TaskModel | None:
        doc = await self._col().find_one_and_update(
            {"task_id": task_id},
            {"$set": data},
            return_document=ReturnDocument.AFTER,
        )
        return self._doc_to_model(doc) if doc else None

    async def toggle_done(self, task_id: str) -> TaskModel | None:
        current = await self.get_by_id(task_id)
        if current is None:
            return None
        new_done = not current.is_done
        patch: dict[str, Any] = {"is_done": new_done}
        patch["completed_at"] = datetime.utcnow() if new_done else None
        return await self.update(task_id, patch)

    async def delete(self, task_id: str) -> bool:
        result = await self._col().delete_one({"task_id": task_id})
        return result.deleted_count > 0
