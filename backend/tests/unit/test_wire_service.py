from unittest.mock import AsyncMock, MagicMock

import pytest

from app.core.exceptions import EntityInUseError, EntityNotFoundError
from app.models.wire import WireMaterial, WireModel
from app.services.wire_service import WireService


def _wire(wire_id: str = "W001") -> WireModel:
    return WireModel(
        wire_id=wire_id,
        gauge_awg=14,
        material=WireMaterial.COPPER,
        color="red",
        length_mm=500.0,
        insulation_rating_v=600.0,
    )


@pytest.fixture
def wire_repo() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def drawing_repo() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def svc(wire_repo: AsyncMock, drawing_repo: AsyncMock) -> WireService:
    return WireService(wire_repo=wire_repo, drawing_repo=drawing_repo)


async def test_get_wire_returns_model(svc: WireService, wire_repo: AsyncMock) -> None:
    wire_repo.get_by_id.return_value = _wire()
    result = await svc.get_wire("W001")
    assert result.wire_id == "W001"


async def test_get_wire_not_found_raises_404(svc: WireService, wire_repo: AsyncMock) -> None:
    wire_repo.get_by_id.return_value = None
    with pytest.raises(EntityNotFoundError):
        await svc.get_wire("W999")


async def test_update_wire_not_found_raises_404(svc: WireService, wire_repo: AsyncMock) -> None:
    wire_repo.update.return_value = None
    with pytest.raises(EntityNotFoundError):
        await svc.update_wire("W999", {"color": "blue"})


async def test_delete_wire_in_use_raises_409(
    svc: WireService, wire_repo: AsyncMock, drawing_repo: AsyncMock
) -> None:
    drawing_repo.get_by_wire_id.return_value = [MagicMock(drawing_id="D001")]
    with pytest.raises(EntityInUseError):
        await svc.delete_wire("W001")
    wire_repo.delete.assert_not_called()


async def test_delete_wire_not_found_raises_404(
    svc: WireService, wire_repo: AsyncMock, drawing_repo: AsyncMock
) -> None:
    drawing_repo.get_by_wire_id.return_value = []
    wire_repo.delete.return_value = False
    with pytest.raises(EntityNotFoundError):
        await svc.delete_wire("W999")


async def test_delete_wire_happy_path(
    svc: WireService, wire_repo: AsyncMock, drawing_repo: AsyncMock
) -> None:
    drawing_repo.get_by_wire_id.return_value = []
    wire_repo.delete.return_value = True
    await svc.delete_wire("W001")
    wire_repo.delete.assert_called_once_with("W001")
