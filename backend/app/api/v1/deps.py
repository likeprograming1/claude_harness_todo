from app.repositories.connector_repository import ConnectorRepository
from app.repositories.harness_drawing_repository import HarnessDrawingRepository
from app.repositories.wire_repository import WireRepository
from app.services.connector_service import ConnectorService
from app.services.harness_drawing_service import HarnessDrawingService
from app.services.wire_service import WireService


def get_wire_service() -> WireService:
    return WireService(wire_repo=WireRepository(), drawing_repo=HarnessDrawingRepository())


def get_connector_service() -> ConnectorService:
    return ConnectorService(connector_repo=ConnectorRepository())


def get_drawing_service() -> HarnessDrawingService:
    return HarnessDrawingService(
        drawing_repo=HarnessDrawingRepository(),
        wire_repo=WireRepository(),
        connector_repo=ConnectorRepository(),
    )
