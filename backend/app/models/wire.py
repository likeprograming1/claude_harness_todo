from dataclasses import dataclass, field
from enum import StrEnum

from app.core.types import AWG_AMPACITY_TABLE


class WireMaterial(StrEnum):
    COPPER = "copper"
    ALUMINUM = "aluminum"
    COPPER_CLAD_ALUMINUM = "copper_clad_aluminum"


@dataclass
class WireModel:
    wire_id: str
    gauge_awg: int
    material: WireMaterial
    color: str
    length_mm: float
    insulation_rating_v: float
    mongo_id: str | None = None
    # Computed from AWG ampacity table in __post_init__; stored to MongoDB for queryability
    max_current_a: float = field(init=False, default=0.0)

    def __post_init__(self) -> None:
        self.max_current_a = AWG_AMPACITY_TABLE[self.gauge_awg]
