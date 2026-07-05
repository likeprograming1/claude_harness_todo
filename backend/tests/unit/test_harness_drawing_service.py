from unittest.mock import AsyncMock

import pytest

from app.core.exceptions import EntityNotFoundError, HarnessValidationError
from app.models.connector import ConnectorGender, ConnectorModel, WaterproofStatus
from app.models.harness_drawing import CircuitModel, HarnessDrawingModel
from app.models.wire import WireMaterial, WireModel
from app.services.harness_drawing_service import HarnessDrawingService


def _drawing(
    revision: str = "Rev.A",
    circuits: list[CircuitModel] | None = None,
    wire_ids: list[str] | None = None,
    connector_ids: list[str] | None = None,
) -> HarnessDrawingModel:
    return HarnessDrawingModel(
        drawing_id="D001",
        revision=revision,
        title="Test Drawing",
        wire_ids=wire_ids or ["W001"],
        connector_ids=connector_ids or ["J1", "J2"],
        circuits=circuits or [],
    )


def _wire(wire_id: str = "W001") -> WireModel:
    return WireModel(
        wire_id=wire_id,
        gauge_awg=14,
        material=WireMaterial.COPPER,
        color="red",
        length_mm=500.0,
        insulation_rating_v=600.0,
    )


def _connector(connector_id: str = "J1", pin_count: int = 4) -> ConnectorModel:
    return ConnectorModel(
        connector_id=connector_id,
        manufacturer="AMP",
        pin_count=pin_count,
        housing_type="Rectangular",
        gender=ConnectorGender.MALE,
        waterproof_status=WaterproofStatus.NOT_WATERPROOF,
    )


def _circuit(
    circuit_id: str = "C1",
    from_pin: int = 1,
    to_pin: int = 1,
    from_conn: str = "J1",
    to_conn: str = "J2",
) -> CircuitModel:
    return CircuitModel(
        circuit_id=circuit_id,
        from_connector_id=from_conn,
        from_connector_pin=from_pin,
        to_connector_id=to_conn,
        to_connector_pin=to_pin,
        wire_id="W001",
        signal_name="SIG",
    )


@pytest.fixture
def drawing_repo() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def wire_repo() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def connector_repo() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def svc(
    drawing_repo: AsyncMock, wire_repo: AsyncMock, connector_repo: AsyncMock
) -> HarnessDrawingService:
    return HarnessDrawingService(
        drawing_repo=drawing_repo,
        wire_repo=wire_repo,
        connector_repo=connector_repo,
    )


# --- update_drawing ---

async def test_update_auto_bumps_revision(
    svc: HarnessDrawingService, drawing_repo: AsyncMock
) -> None:
    drawing_repo.get_by_id.return_value = _drawing(revision="Rev.A")
    drawing_repo.update.return_value = _drawing(revision="Rev.B")

    result = await svc.update_drawing("D001", {"title": "New"})

    assert result.revision == "Rev.B"
    sent = drawing_repo.update.call_args[0][1]
    assert sent["revision"] == "Rev.B"


async def test_update_explicit_revision_skips_bump(
    svc: HarnessDrawingService, drawing_repo: AsyncMock
) -> None:
    drawing_repo.update.return_value = _drawing(revision="Rev.C")

    result = await svc.update_drawing("D001", {"revision": "Rev.C"})

    drawing_repo.get_by_id.assert_not_called()
    assert result.revision == "Rev.C"


async def test_update_revision_z_raises_error(
    svc: HarnessDrawingService, drawing_repo: AsyncMock
) -> None:
    drawing_repo.get_by_id.return_value = _drawing(revision="Rev.Z")
    with pytest.raises(HarnessValidationError, match="Rev.Z"):
        await svc.update_drawing("D001", {})


async def test_update_not_found_raises_404(
    svc: HarnessDrawingService, drawing_repo: AsyncMock
) -> None:
    drawing_repo.get_by_id.return_value = None
    with pytest.raises(EntityNotFoundError):
        await svc.update_drawing("D999", {})


# --- validate_drawing ---

async def test_validate_not_found_raises_404(
    svc: HarnessDrawingService, drawing_repo: AsyncMock
) -> None:
    drawing_repo.get_by_id.return_value = None
    with pytest.raises(EntityNotFoundError):
        await svc.validate_drawing("D999")


async def test_validate_valid_drawing(
    svc: HarnessDrawingService,
    drawing_repo: AsyncMock,
    wire_repo: AsyncMock,
    connector_repo: AsyncMock,
) -> None:
    drawing_repo.get_by_id.return_value = _drawing(circuits=[_circuit(from_pin=1, to_pin=1)])
    wire_repo.get_many.return_value = [_wire()]
    connector_repo.get_many.return_value = [_connector("J1", 4), _connector("J2", 4)]

    report = await svc.validate_drawing("D001")

    assert report.valid is True
    assert report.errors == []


async def test_validate_pin_out_of_bounds(
    svc: HarnessDrawingService,
    drawing_repo: AsyncMock,
    wire_repo: AsyncMock,
    connector_repo: AsyncMock,
) -> None:
    drawing_repo.get_by_id.return_value = _drawing(
        circuits=[_circuit(from_pin=5)]  # pin_count=4
    )
    wire_repo.get_many.return_value = [_wire()]
    connector_repo.get_many.return_value = [_connector("J1", 4), _connector("J2", 4)]

    report = await svc.validate_drawing("D001")

    assert report.valid is False
    assert any("pin_count" in e for e in report.errors)


async def test_validate_duplicate_pin_assignment(
    svc: HarnessDrawingService,
    drawing_repo: AsyncMock,
    wire_repo: AsyncMock,
    connector_repo: AsyncMock,
) -> None:
    c1 = _circuit("C1", from_pin=1, to_pin=1)
    c2 = _circuit("C2", from_pin=1, to_pin=2)  # same from_connector J1 pin 1 as C1
    drawing_repo.get_by_id.return_value = _drawing(circuits=[c1, c2])
    wire_repo.get_many.return_value = [_wire()]
    connector_repo.get_many.return_value = [_connector("J1", 4), _connector("J2", 4)]

    report = await svc.validate_drawing("D001")

    assert report.valid is False
    assert any("already assigned" in e for e in report.errors)


async def test_validate_missing_wire_id(
    svc: HarnessDrawingService,
    drawing_repo: AsyncMock,
    wire_repo: AsyncMock,
    connector_repo: AsyncMock,
) -> None:
    drawing_repo.get_by_id.return_value = _drawing(wire_ids=["W_MISSING"])
    wire_repo.get_many.return_value = []  # nothing found
    connector_repo.get_many.return_value = [_connector("J1", 4), _connector("J2", 4)]

    report = await svc.validate_drawing("D001")

    assert report.valid is False
    assert any("Wire IDs not found" in e for e in report.errors)
