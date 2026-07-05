import dataclasses
from typing import Any

from pymongo import ReturnDocument
from pymongo.errors import DuplicateKeyError

from app.core.exceptions import DuplicateEntityError
from app.models.connector import ConnectorGender, ConnectorModel, WaterproofStatus
from app.repositories.base import BaseRepository, _id_to_str


class ConnectorRepository(BaseRepository[ConnectorModel]):
    collection_name = "connectors"

    def _doc_to_model(self, doc: dict[str, Any]) -> ConnectorModel:
        return ConnectorModel(
            connector_id=str(doc["connector_id"]),
            manufacturer=str(doc["manufacturer"]),
            pin_count=int(doc["pin_count"]),
            housing_type=str(doc["housing_type"]),
            gender=ConnectorGender(doc["gender"]),
            waterproof_status=WaterproofStatus(doc["waterproof_status"]),
            mating_connector_id=str(doc["mating_connector_id"])
            if doc.get("mating_connector_id") is not None
            else None,
            mongo_id=_id_to_str(doc["_id"]),
        )

    @staticmethod
    def _model_to_doc(model: ConnectorModel) -> dict[str, Any]:
        d = dataclasses.asdict(model)
        d.pop("mongo_id", None)
        return d

    async def get_by_id(self, connector_id: str) -> ConnectorModel | None:
        doc = await self._col().find_one({"connector_id": connector_id})
        return self._doc_to_model(doc) if doc is not None else None

    async def get_many(self, ids: list[str]) -> list[ConnectorModel]:
        cursor = self._col().find({"connector_id": {"$in": ids}})
        return [self._doc_to_model(doc) async for doc in cursor]

    async def create(self, data: dict[str, Any]) -> ConnectorModel:
        model = ConnectorModel(
            connector_id=str(data["connector_id"]),
            manufacturer=str(data["manufacturer"]),
            pin_count=int(data["pin_count"]),
            housing_type=str(data["housing_type"]),
            gender=ConnectorGender(data["gender"]),
            waterproof_status=WaterproofStatus(
                data.get("waterproof_status", WaterproofStatus.NOT_WATERPROOF)
            ),
            mating_connector_id=str(data["mating_connector_id"])
            if data.get("mating_connector_id") is not None
            else None,
        )
        doc = self._model_to_doc(model)
        try:
            result = await self._col().insert_one(doc)
        except DuplicateKeyError:
            raise DuplicateEntityError("Connector", "connector_id", model.connector_id) from None
        doc["_id"] = result.inserted_id
        return self._doc_to_model(doc)

    async def update(self, connector_id: str, data: dict[str, Any]) -> ConnectorModel | None:
        doc = await self._col().find_one_and_update(
            {"connector_id": connector_id},
            {"$set": data},
            return_document=ReturnDocument.AFTER,
        )
        return self._doc_to_model(doc) if doc is not None else None

    async def delete(self, connector_id: str) -> bool:
        result = await self._col().delete_one({"connector_id": connector_id})
        return bool(result.deleted_count > 0)
