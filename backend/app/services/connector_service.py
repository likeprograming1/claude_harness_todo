from typing import Any

from app.core.exceptions import EntityInUseError, EntityNotFoundError, HarnessValidationError
from app.models.connector import ConnectorModel
from app.repositories.connector_repository import ConnectorRepository


class ConnectorService:
    def __init__(self, connector_repo: ConnectorRepository) -> None:
        self._connector_repo = connector_repo

    async def create_connector(self, data: dict[str, Any]) -> ConnectorModel:
        return await self._connector_repo.create(data)

    async def get_connector(self, connector_id: str) -> ConnectorModel:
        connector = await self._connector_repo.get_by_id(connector_id)
        if connector is None:
            raise EntityNotFoundError("Connector", connector_id)
        return connector

    async def list_connectors(self) -> list[ConnectorModel]:
        return await self._connector_repo.list_all()

    async def update_connector(self, connector_id: str, data: dict[str, Any]) -> ConnectorModel:
        connector = await self._connector_repo.update(connector_id, data)
        if connector is None:
            raise EntityNotFoundError("Connector", connector_id)
        return connector

    async def delete_connector(self, connector_id: str) -> None:
        deleted = await self._connector_repo.delete(connector_id)
        if not deleted:
            raise EntityNotFoundError("Connector", connector_id)

    async def link_mating_connector(
        self, a_id: str, b_id: str
    ) -> tuple[ConnectorModel, ConnectorModel]:
        if a_id == b_id:
            raise HarnessValidationError(errors=["A connector cannot mate with itself."])

        a = await self._connector_repo.get_by_id(a_id)
        if a is None:
            raise EntityNotFoundError("Connector", a_id)
        b = await self._connector_repo.get_by_id(b_id)
        if b is None:
            raise EntityNotFoundError("Connector", b_id)

        # Idempotent: already correctly mated to each other
        if a.mating_connector_id == b_id and b.mating_connector_id == a_id:
            return a, b

        if a.mating_connector_id is not None and a.mating_connector_id != b_id:
            raise EntityInUseError(
                "Connector", a_id, f"already mated with '{a.mating_connector_id}'"
            )
        if b.mating_connector_id is not None and b.mating_connector_id != a_id:
            raise EntityInUseError(
                "Connector", b_id, f"already mated with '{b.mating_connector_id}'"
            )

        updated_a = await self._connector_repo.update(a_id, {"mating_connector_id": b_id})
        updated_b = await self._connector_repo.update(b_id, {"mating_connector_id": a_id})

        if updated_a is None:
            raise EntityNotFoundError("Connector", a_id)
        if updated_b is None:
            raise EntityNotFoundError("Connector", b_id)

        return updated_a, updated_b
