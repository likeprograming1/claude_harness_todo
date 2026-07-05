from dataclasses import dataclass, field


@dataclass
class CircuitModel:
    circuit_id: str
    from_connector_id: str
    from_connector_pin: int
    to_connector_id: str
    to_connector_pin: int
    wire_id: str
    signal_name: str


@dataclass
class HarnessDrawingModel:
    drawing_id: str
    revision: str
    title: str
    wire_ids: list[str] = field(default_factory=list)
    connector_ids: list[str] = field(default_factory=list)
    circuits: list[CircuitModel] = field(default_factory=list)
    mongo_id: str | None = None
