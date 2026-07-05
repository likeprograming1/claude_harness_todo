import dataclasses
from typing import Any

from pymongo import ReturnDocument
from pymongo.errors import DuplicateKeyError

from app.core.exceptions import DuplicateEntityError
from app.core.types import AWG_AMPACITY_TABLE
from app.models.wire import WireMaterial, WireModel
from app.repositories.base import BaseRepository, _id_to_str


class WireRepository(BaseRepository[WireModel]):
    collection_name = "wires"

    def _doc_to_model(self, doc: dict[str, Any]) -> WireModel:
        return WireModel(
            wire_id=str(doc["wire_id"]),
            gauge_awg=int(doc["gauge_awg"]),
            material=WireMaterial(doc["material"]),
            color=str(doc["color"]),
            length_mm=float(doc["length_mm"]),
            insulation_rating_v=float(doc["insulation_rating_v"]),
            mongo_id=_id_to_str(doc["_id"]),
        )

    @staticmethod
    def _model_to_doc(model: WireModel) -> dict[str, Any]:
        d = dataclasses.asdict(model)
        d.pop("mongo_id", None)
        return d

    async def list_all(self) -> list[WireModel]:
        cursor = self._col().find({})
        return [self._doc_to_model(doc) async for doc in cursor]

    async def get_by_id(self, wire_id: str) -> WireModel | None:
        doc = await self._col().find_one({"wire_id": wire_id})
        return self._doc_to_model(doc) if doc is not None else None

    async def get_many(self, ids: list[str]) -> list[WireModel]:
        cursor = self._col().find({"wire_id": {"$in": ids}})
        return [self._doc_to_model(doc) async for doc in cursor]

    async def create(self, data: dict[str, Any]) -> WireModel:
        model = WireModel(
            wire_id=str(data["wire_id"]),
            gauge_awg=int(data["gauge_awg"]),
            material=WireMaterial(data["material"]),
            color=str(data["color"]),
            length_mm=float(data["length_mm"]),
            insulation_rating_v=float(data["insulation_rating_v"]),
        )
        doc = self._model_to_doc(model)
        try:
            result = await self._col().insert_one(doc)
        except DuplicateKeyError:
            raise DuplicateEntityError("Wire", "wire_id", model.wire_id) from None
        doc["_id"] = result.inserted_id
        return self._doc_to_model(doc)

    async def update(self, wire_id: str, data: dict[str, Any]) -> WireModel | None:
        # Keep max_current_a in sync when gauge_awg changes
        if "gauge_awg" in data:
            data = {**data, "max_current_a": AWG_AMPACITY_TABLE[int(data["gauge_awg"])]}
        doc = await self._col().find_one_and_update(
            {"wire_id": wire_id},
            {"$set": data},
            return_document=ReturnDocument.AFTER,
        )
        return self._doc_to_model(doc) if doc is not None else None

    async def delete(self, wire_id: str) -> bool:
        result = await self._col().delete_one({"wire_id": wire_id})
        return bool(result.deleted_count > 0)
