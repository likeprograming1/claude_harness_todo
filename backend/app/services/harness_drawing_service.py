from typing import Any

from app.core.exceptions import EntityNotFoundError, HarnessValidationError
from app.models.harness_drawing import HarnessDrawingModel
from app.repositories.connector_repository import ConnectorRepository
from app.repositories.harness_drawing_repository import HarnessDrawingRepository
from app.repositories.wire_repository import WireRepository
from app.schemas.harness_drawing import ValidationReport


class HarnessDrawingService:
    def __init__(
        self,
        drawing_repo: HarnessDrawingRepository,
        wire_repo: WireRepository,
        connector_repo: ConnectorRepository,
    ) -> None:
        self._drawing_repo = drawing_repo
        self._wire_repo = wire_repo
        self._connector_repo = connector_repo

    async def create_drawing(self, data: dict[str, Any]) -> HarnessDrawingModel:
        return await self._drawing_repo.create(data)

    async def get_drawing(self, drawing_id: str) -> HarnessDrawingModel:
        drawing = await self._drawing_repo.get_by_id(drawing_id)
        if drawing is None:
            raise EntityNotFoundError("HarnessDrawing", drawing_id)
        return drawing

    async def list_drawings(self) -> list[HarnessDrawingModel]:
        return await self._drawing_repo.list_all()

    async def update_drawing(self, drawing_id: str, data: dict[str, Any]) -> HarnessDrawingModel:
        if "revision" not in data:
            current = await self._drawing_repo.get_by_id(drawing_id)
            if current is None:
                raise EntityNotFoundError("HarnessDrawing", drawing_id)
            current_letter = current.revision[-1]  # "Rev.A"[-1] == "A"
            if current_letter == "Z":
                raise HarnessValidationError(
                    errors=["Revision 'Rev.Z' cannot be bumped further."]
                )
            data = {**data, "revision": f"Rev.{chr(ord(current_letter) + 1)}"}

        drawing = await self._drawing_repo.update(drawing_id, data)
        if drawing is None:
            raise EntityNotFoundError("HarnessDrawing", drawing_id)
        return drawing

    async def delete_drawing(self, drawing_id: str) -> None:
        deleted = await self._drawing_repo.delete(drawing_id)
        if not deleted:
            raise EntityNotFoundError("HarnessDrawing", drawing_id)

    async def validate_drawing(self, drawing_id: str) -> ValidationReport:
        drawing = await self._drawing_repo.get_by_id(drawing_id)
        if drawing is None:
            raise EntityNotFoundError("HarnessDrawing", drawing_id)

        errors: list[str] = []

        # Collect all IDs referenced across top-level lists and circuits
        all_wire_ids: set[str] = set(drawing.wire_ids)
        all_connector_ids: set[str] = set(drawing.connector_ids)
        for circuit in drawing.circuits:
            all_wire_ids.add(circuit.wire_id)
            all_connector_ids.add(circuit.from_connector_id)
            all_connector_ids.add(circuit.to_connector_id)

        wire_map = {
            w.wire_id: w for w in await self._wire_repo.get_many(list(all_wire_ids))
        }
        connector_map = {
            c.connector_id: c
            for c in await self._connector_repo.get_many(list(all_connector_ids))
        }

        # Check 1: reference existence
        missing_wires = sorted(all_wire_ids - set(wire_map))
        if missing_wires:
            errors.append(f"Wire IDs not found: {missing_wires}")

        missing_connectors = sorted(all_connector_ids - set(connector_map))
        if missing_connectors:
            errors.append(f"Connector IDs not found: {missing_connectors}")

        # Checks 2 & 4: pin bounds + duplicate pin assignment (skip missing connectors)
        pin_usage: dict[tuple[str, int], str] = {}  # (connector_id, pin) -> circuit_id
        for circuit in drawing.circuits:
            for conn_id, pin, label in [
                (circuit.from_connector_id, circuit.from_connector_pin, "from"),
                (circuit.to_connector_id, circuit.to_connector_pin, "to"),
            ]:
                connector = connector_map.get(conn_id)
                if connector is None:
                    continue
                if pin > connector.pin_count:
                    errors.append(
                        f"Circuit {circuit.circuit_id}: {label}_connector_pin {pin} "
                        f"exceeds {conn_id} pin_count {connector.pin_count}"
                    )
                key = (conn_id, pin)
                if key in pin_usage:
                    errors.append(
                        f"Circuit {circuit.circuit_id}: pin {pin} of connector {conn_id} "
                        f"already assigned to circuit {pin_usage[key]}"
                    )
                else:
                    pin_usage[key] = circuit.circuit_id

        # Check 3: duplicate circuit_id in stored data
        seen_ids: set[str] = set()
        for circuit in drawing.circuits:
            if circuit.circuit_id in seen_ids:
                errors.append(f"Duplicate circuit_id: {circuit.circuit_id}")
            seen_ids.add(circuit.circuit_id)

        return ValidationReport(
            drawing_id=drawing_id,
            valid=not errors,
            errors=errors,
        )
