import dataclasses
from datetime import date
from typing import Any

from pymongo.errors import DuplicateKeyError

from app.core.exceptions import DuplicateEntityError
from app.models.milestone import MilestoneModel
from app.repositories.base import BaseRepository, _id_to_str


class MilestoneRepository(BaseRepository[MilestoneModel]):
    collection_name = "milestones"

    def _doc_to_model(self, doc: dict[str, Any]) -> MilestoneModel:
        achieved = doc["achieved_at"]
        if isinstance(achieved, str):
            achieved = date.fromisoformat(achieved)
        elif isinstance(achieved, date):
            pass
        else:
            achieved = date.fromisoformat(str(achieved)[:10])

        return MilestoneModel(
            milestone_id=str(doc["milestone_id"]),
            title=str(doc["title"]),
            description=str(doc["description"]),
            achieved_at=achieved,
            mongo_id=_id_to_str(doc["_id"]),
        )

    @staticmethod
    def _model_to_doc(model: MilestoneModel) -> dict[str, Any]:
        d = dataclasses.asdict(model)
        d.pop("mongo_id", None)
        d["achieved_at"] = model.achieved_at.isoformat()
        return d

    async def list_all(self) -> list[MilestoneModel]:
        cursor = self._col().find({}).sort("achieved_at", -1)
        return [self._doc_to_model(doc) async for doc in cursor]

    async def get_by_id(self, milestone_id: str) -> MilestoneModel | None:
        doc = await self._col().find_one({"milestone_id": milestone_id})
        return self._doc_to_model(doc) if doc else None

    async def exists(self, milestone_id: str) -> bool:
        return await self._col().count_documents({"milestone_id": milestone_id}) > 0

    async def create(self, data: dict[str, Any]) -> MilestoneModel:
        model = MilestoneModel(
            milestone_id=str(data["milestone_id"]),
            title=str(data["title"]),
            description=str(data["description"]),
            achieved_at=data["achieved_at"] if isinstance(data["achieved_at"], date)
            else date.fromisoformat(str(data["achieved_at"])),
        )
        doc = self._model_to_doc(model)
        try:
            result = await self._col().insert_one(doc)
        except DuplicateKeyError:
            raise DuplicateEntityError(
                "Milestone", "milestone_id", model.milestone_id
            ) from None
        doc["_id"] = result.inserted_id
        return self._doc_to_model(doc)
