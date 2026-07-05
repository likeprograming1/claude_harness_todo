from unittest.mock import AsyncMock

import pytest

from app.core.exceptions import EntityInUseError, EntityNotFoundError, HarnessValidationError
from app.models.connector import ConnectorGender, ConnectorModel, WaterproofStatus
from app.services.connector_service import ConnectorService


def _connector(connector_id: str = "C001", mating_connector_id: str | None = None) -> ConnectorModel:
    return ConnectorModel(
        connector_id=connector_id,
        manufacturer="AMP",
        pin_count=4,
        housing_type="Rectangular",
        gender=ConnectorGender.MALE,
        waterproof_status=WaterproofStatus.NOT_WATERPROOF,
        mating_connector_id=mating_connector_id,
    )


@pytest.fixture
def connector_repo() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def svc(connector_repo: AsyncMock) -> ConnectorService:
    return ConnectorService(connector_repo=connector_repo)


async def test_get_connector_not_found(svc: ConnectorService, connector_repo: AsyncMock) -> None:
    connector_repo.get_by_id.return_value = None
    with pytest.raises(EntityNotFoundError):
        await svc.get_connector("C999")


async def test_delete_connector_not_found(svc: ConnectorService, connector_repo: AsyncMock) -> None:
    connector_repo.delete.return_value = False
    with pytest.raises(EntityNotFoundError):
        await svc.delete_connector("C999")


async def test_link_mating_self_raises_422(svc: ConnectorService) -> None:
    with pytest.raises(HarnessValidationError):
        await svc.link_mating_connector("C001", "C001")


async def test_link_mating_a_not_found(svc: ConnectorService, connector_repo: AsyncMock) -> None:
    connector_repo.get_by_id.return_value = None
    with pytest.raises(EntityNotFoundError):
        await svc.link_mating_connector("C999", "C001")


async def test_link_mating_b_not_found(svc: ConnectorService, connector_repo: AsyncMock) -> None:
    connector_repo.get_by_id.side_effect = [_connector("C001"), None]
    with pytest.raises(EntityNotFoundError):
        await svc.link_mating_connector("C001", "C999")


async def test_link_mating_a_already_mated_raises_409(
    svc: ConnectorService, connector_repo: AsyncMock
) -> None:
    a = _connector("C001", mating_connector_id="C999")  # mated to someone else
    b = _connector("C002")
    connector_repo.get_by_id.side_effect = [a, b]
    with pytest.raises(EntityInUseError):
        await svc.link_mating_connector("C001", "C002")


async def test_link_mating_b_already_mated_raises_409(
    svc: ConnectorService, connector_repo: AsyncMock
) -> None:
    a = _connector("C001")
    b = _connector("C002", mating_connector_id="C999")  # mated to someone else
    connector_repo.get_by_id.side_effect = [a, b]
    with pytest.raises(EntityInUseError):
        await svc.link_mating_connector("C001", "C002")


async def test_link_mating_idempotent(
    svc: ConnectorService, connector_repo: AsyncMock
) -> None:
    a = _connector("C001", mating_connector_id="C002")
    b = _connector("C002", mating_connector_id="C001")
    connector_repo.get_by_id.side_effect = [a, b]
    result_a, result_b = await svc.link_mating_connector("C001", "C002")
    connector_repo.update.assert_not_called()
    assert result_a.connector_id == "C001"
    assert result_b.connector_id == "C002"


async def test_link_mating_symmetric(
    svc: ConnectorService, connector_repo: AsyncMock
) -> None:
    a = _connector("C001")
    b = _connector("C002")
    updated_a = _connector("C001", mating_connector_id="C002")
    updated_b = _connector("C002", mating_connector_id="C001")

    connector_repo.get_by_id.side_effect = [a, b]
    connector_repo.update.side_effect = [updated_a, updated_b]

    result_a, result_b = await svc.link_mating_connector("C001", "C002")
    assert result_a.mating_connector_id == "C002"
    assert result_b.mating_connector_id == "C001"
    assert connector_repo.update.call_count == 2
