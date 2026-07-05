import logging

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.core.types import VALID_AWG_GAUGES
from app.models.wire import WireMaterial

logger = logging.getLogger(__name__)

_SORTED_AWG = sorted(VALID_AWG_GAUGES, reverse=True)  # 30 → 0, descending for readability


class WireCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    wire_id: str = Field(min_length=1, max_length=50)
    gauge_awg: int
    material: WireMaterial
    color: str = Field(min_length=1, max_length=30)
    length_mm: float = Field(gt=0, description="Wire length in millimetres")
    insulation_rating_v: float = Field(gt=0, description="Insulation voltage rating in Volts")

    @field_validator("gauge_awg")
    @classmethod
    def validate_awg_gauge(cls, v: int) -> int:
        if v not in VALID_AWG_GAUGES:
            raise ValueError(f"{v} AWG is not a valid gauge. Allowed values: {_SORTED_AWG}")
        return v

    @field_validator("insulation_rating_v")
    @classmethod
    def warn_low_voltage_rating(cls, v: float) -> float:
        if v < 12.0:
            logger.warning("insulation_rating_v=%.1f V is below the 12 V automotive minimum", v)
        return v


class WireUpdate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    gauge_awg: int | None = None
    material: WireMaterial | None = None
    color: str | None = Field(default=None, min_length=1, max_length=30)
    length_mm: float | None = Field(default=None, gt=0)
    insulation_rating_v: float | None = Field(default=None, gt=0)

    @field_validator("gauge_awg")
    @classmethod
    def validate_awg_gauge(cls, v: int | None) -> int | None:
        if v is not None and v not in VALID_AWG_GAUGES:
            raise ValueError(f"{v} AWG is not a valid gauge. Allowed values: {_SORTED_AWG}")
        return v

    @field_validator("insulation_rating_v")
    @classmethod
    def warn_low_voltage_rating(cls, v: float | None) -> float | None:
        if v is not None and v < 12.0:
            logger.warning("insulation_rating_v=%.1f V is below the 12 V automotive minimum", v)
        return v


class WireResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: str = Field(description="MongoDB document id (mapped from _id)")
    wire_id: str
    gauge_awg: int
    material: WireMaterial
    color: str
    length_mm: float
    insulation_rating_v: float
    max_current_a: float = Field(
        description="Maximum continuous current in Amperes (SAE chassis wiring)"
    )
