from dataclasses import dataclass
from enum import StrEnum


class ConnectorGender(StrEnum):
    MALE = "male"
    FEMALE = "female"
    NEUTRAL = "neutral"


class WaterproofStatus(StrEnum):
    NOT_WATERPROOF = "not_waterproof"
    IP54 = "IP54"
    IP67 = "IP67"
    IP68 = "IP68"


@dataclass
class ConnectorModel:
    connector_id: str
    manufacturer: str
    pin_count: int
    housing_type: str
    gender: ConnectorGender
    waterproof_status: WaterproofStatus
    mating_connector_id: str | None = None
    mongo_id: str | None = None
