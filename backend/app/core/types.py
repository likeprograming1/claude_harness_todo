from typing import Any

from bson import ObjectId
from pydantic import GetCoreSchemaHandler
from pydantic_core import core_schema

# Standard AWG gauges used in automotive/harness wiring (largest to smallest wire)
VALID_AWG_GAUGES: frozenset[int] = frozenset(
    {0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30}
)

# Chassis-wiring ampacity (A) per AWG gauge — based on SAE/ISO automotive standards
AWG_AMPACITY_TABLE: dict[int, float] = {
    0: 245.0,
    2: 185.0,
    4: 125.0,
    6: 80.0,
    8: 55.0,
    10: 30.0,
    12: 20.0,
    14: 15.0,
    16: 13.0,
    18: 10.0,
    20: 5.0,
    22: 3.0,
    24: 2.0,
    26: 1.0,
    28: 0.5,
    30: 0.3,
}


class PyObjectId(str):
    """Pydantic v2 custom type: accepts bson.ObjectId or a valid 24-hex string, serialises as str."""

    @classmethod
    def __get_pydantic_core_schema__(
        cls,
        source_type: Any,
        handler: GetCoreSchemaHandler,
    ) -> core_schema.CoreSchema:
        return core_schema.no_info_plain_validator_function(
            function=cls._validate,
            serialization=core_schema.to_string_ser_schema(),
        )

    @classmethod
    def _validate(cls, value: Any) -> "PyObjectId":
        if isinstance(value, ObjectId):
            return cls(str(value))
        if isinstance(value, str) and ObjectId.is_valid(value):
            return cls(value)
        raise ValueError(f"Invalid ObjectId: {value!r}")
