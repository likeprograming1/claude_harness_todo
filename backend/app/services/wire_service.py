from typing import Any

from app.core.exceptions import EntityInUseError, EntityNotFoundError
from app.models.wire import WireModel
from app.repositories.harness_drawing_repository import HarnessDrawingRepository
from app.repositories.wire_repository import WireRepository


class WireService:
    def __init__(
        self,
        wire_repo: WireRepository,
        drawing_repo: HarnessDrawingRepository,
    ) -> None:
        self._wire_repo = wire_repo
        self._drawing_repo = drawing_repo

    async def create_wire(self, data: dict[str, Any]) -> WireModel:
        return await self._wire_repo.create(data)

    async def get_wire(self, wire_id: str) -> WireModel:
        wire = await self._wire_repo.get_by_id(wire_id)
        if wire is None:
            raise EntityNotFoundError("Wire", wire_id)
        return wire

    async def list_wires(self) -> list[WireModel]:
        return await self._wire_repo.list_all()

    async def update_wire(self, wire_id: str, data: dict[str, Any]) -> WireModel:
        wire = await self._wire_repo.update(wire_id, data)
        if wire is None:
            raise EntityNotFoundError("Wire", wire_id)
        return wire

    async def delete_wire(self, wire_id: str) -> None:
        drawings = await self._drawing_repo.get_by_wire_id(wire_id)
        if drawings:
            ids = ", ".join(d.drawing_id for d in drawings)
            raise EntityInUseError("Wire", wire_id, f"referenced by drawing(s): {ids}")
        deleted = await self._wire_repo.delete(wire_id)
        if not deleted:
            raise EntityNotFoundError("Wire", wire_id)
