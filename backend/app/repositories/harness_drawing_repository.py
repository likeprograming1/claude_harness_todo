import dataclasses
from typing import Any

from pymongo import ReturnDocument
from pymongo.errors import DuplicateKeyError

from app.core.database import get_db
from app.core.exceptions import DuplicateEntityError, HarnessValidationError
from app.models.harness_drawing import CircuitModel, HarnessDrawingModel
from app.repositories.base import BaseRepository, _id_to_str


class HarnessDrawingRepository(BaseRepository[HarnessDrawingModel]):
    collection_name = "harness_drawings"

    def _doc_to_circuit(self, d: dict[str, Any]) -> CircuitModel:
        return CircuitModel(
            circuit_id=str(d["circuit_id"]),
            from_connector_id=str(d["from_connector_id"]),
            from_connector_pin=int(d["from_connector_pin"]),
            to_connector_id=str(d["to_connector_id"]),
            to_connector_pin=int(d["to_connector_pin"]),
            wire_id=str(d["wire_id"]),
            signal_name=str(d["signal_name"]),
        )

    def _doc_to_model(self, doc: dict[str, Any]) -> HarnessDrawingModel:
        return HarnessDrawingModel(
            drawing_id=str(doc["drawing_id"]),
            revision=str(doc["revision"]),
            title=str(doc["title"]),
            wire_ids=[str(w) for w in doc.get("wire_ids", [])],
            connector_ids=[str(c) for c in doc.get("connector_ids", [])],
            circuits=[self._doc_to_circuit(c) for c in doc.get("circuits", [])],
            mongo_id=_id_to_str(doc["_id"]),
        )

    @staticmethod
    def _model_to_doc(model: HarnessDrawingModel) -> dict[str, Any]:
        d = dataclasses.asdict(model)
        d.pop("mongo_id", None)
        return d

    async def _check_refs(
        self,
        wire_ids: set[str],
        connector_ids: set[str],
    ) -> None:
        """Verify that all referenced wire and connector IDs exist in the database."""
        db = get_db()
        errors: list[str] = []

        if wire_ids:
            cursor = db["wires"].find(
                {"wire_id": {"$in": list(wire_ids)}},
                {"wire_id": 1, "_id": 0},
            )
            found_wires: set[str] = {str(doc["wire_id"]) async for doc in cursor}
            missing = sorted(wire_ids - found_wires)
            if missing:
                errors.append(f"Wire IDs not found: {missing}")

        if connector_ids:
            cursor = db["connectors"].find(
                {"connector_id": {"$in": list(connector_ids)}},
                {"connector_id": 1, "_id": 0},
            )
            found_connectors: set[str] = {str(doc["connector_id"]) async for doc in cursor}
            missing = sorted(connector_ids - found_connectors)
            if missing:
                errors.append(f"Connector IDs not found: {missing}")

        if errors:
            raise HarnessValidationError(errors=errors)

    def _collect_refs(
        self,
        wire_ids: list[str],
        connector_ids: list[str],
        circuits: list[CircuitModel],
    ) -> tuple[set[str], set[str]]:
        """Collect all wire and connector IDs referenced in both top-level lists and circuits."""
        all_wire_ids = set(wire_ids)
        all_connector_ids = set(connector_ids)
        for c in circuits:
            all_wire_ids.add(c.wire_id)
            all_connector_ids.add(c.from_connector_id)
            all_connector_ids.add(c.to_connector_id)
        return all_wire_ids, all_connector_ids

    async def get_by_id(self, drawing_id: str) -> HarnessDrawingModel | None:
        doc = await self._col().find_one({"drawing_id": drawing_id})
        return self._doc_to_model(doc) if doc is not None else None

    async def list_all(self) -> list[HarnessDrawingModel]:
        cursor = self._col().find({})
        return [self._doc_to_model(doc) async for doc in cursor]

    async def create(self, data: dict[str, Any]) -> HarnessDrawingModel:
        raw_circuits: list[dict[str, Any]] = [
            c if isinstance(c, dict) else dataclasses.asdict(c)
            for c in data.get("circuits", [])
        ]
        circuits = [self._doc_to_circuit(c) for c in raw_circuits]
        wire_ids: list[str] = [str(w) for w in data.get("wire_ids", [])]
        connector_ids: list[str] = [str(c) for c in data.get("connector_ids", [])]

        all_wire_ids, all_connector_ids = self._collect_refs(wire_ids, connector_ids, circuits)
        await self._check_refs(all_wire_ids, all_connector_ids)

        model = HarnessDrawingModel(
            drawing_id=str(data["drawing_id"]),
            revision=str(data["revision"]),
            title=str(data["title"]),
            wire_ids=wire_ids,
            connector_ids=connector_ids,
            circuits=circuits,
        )
        doc = self._model_to_doc(model)
        try:
            result = await self._col().insert_one(doc)
        except DuplicateKeyError:
            raise DuplicateEntityError("HarnessDrawing", "drawing_id", model.drawing_id) from None
        doc["_id"] = result.inserted_id
        return self._doc_to_model(doc)

    async def update(self, drawing_id: str, data: dict[str, Any]) -> HarnessDrawingModel | None:
        # Resolve circuits for ref check if circuits are being updated
        circuits: list[CircuitModel] = []
        if "circuits" in data:
            raw_circuits: list[dict[str, Any]] = [
                c if isinstance(c, dict) else dataclasses.asdict(c)
                for c in data["circuits"]
            ]
            circuits = [self._doc_to_circuit(c) for c in raw_circuits]

        wire_ids: list[str] = [str(w) for w in data.get("wire_ids", [])]
        connector_ids: list[str] = [str(c) for c in data.get("connector_ids", [])]

        if wire_ids or connector_ids or circuits:
            all_wire_ids, all_connector_ids = self._collect_refs(
                wire_ids, connector_ids, circuits
            )
            await self._check_refs(all_wire_ids, all_connector_ids)

        # Serialise CircuitModel objects before sending to MongoDB
        if circuits:
            data = {**data, "circuits": [dataclasses.asdict(c) for c in circuits]}

        doc = await self._col().find_one_and_update(
            {"drawing_id": drawing_id},
            {"$set": data},
            return_document=ReturnDocument.AFTER,
        )
        return self._doc_to_model(doc) if doc is not None else None

    async def delete(self, drawing_id: str) -> bool:
        result = await self._col().delete_one({"drawing_id": drawing_id})
        return bool(result.deleted_count > 0)

    async def get_by_wire_id(self, wire_id: str) -> list[HarnessDrawingModel]:
        cursor = self._col().find({"wire_ids": wire_id})
        return [self._doc_to_model(doc) async for doc in cursor]
