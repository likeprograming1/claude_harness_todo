import re

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

# Rev.A through Rev.Z — single uppercase letter only
_REVISION_PATTERN: re.Pattern[str] = re.compile(r"^Rev\.[A-Z]$")


class CircuitSchema(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    circuit_id: str = Field(min_length=1, max_length=50)
    from_connector_id: str = Field(min_length=1, max_length=50)
    from_connector_pin: int = Field(
        gt=0, description="1-indexed pin number on the source connector"
    )
    to_connector_id: str = Field(min_length=1, max_length=50)
    to_connector_pin: int = Field(
        gt=0, description="1-indexed pin number on the destination connector"
    )
    wire_id: str = Field(min_length=1, max_length=50)
    signal_name: str = Field(min_length=1, max_length=100)


class HarnessDrawingCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    drawing_id: str = Field(min_length=1, max_length=50)
    revision: str = Field(min_length=5, max_length=5, description="Format: Rev.[A-Z], e.g. Rev.A")
    title: str = Field(min_length=1, max_length=200)
    wire_ids: list[str] = Field(default_factory=list)
    connector_ids: list[str] = Field(default_factory=list)
    circuits: list[CircuitSchema] = Field(default_factory=list)

    @field_validator("revision")
    @classmethod
    def validate_revision_format(cls, v: str) -> str:
        if not _REVISION_PATTERN.match(v):
            raise ValueError(
                f"revision '{v}' is invalid. Must match Rev.[A-Z] (e.g. Rev.A, Rev.B)."
            )
        return v

    @model_validator(mode="after")
    def validate_circuit_ids_unique(self) -> "HarnessDrawingCreate":
        circuit_ids = [c.circuit_id for c in self.circuits]
        seen: set[str] = set()
        duplicates: list[str] = []
        for cid in circuit_ids:
            if cid in seen:
                duplicates.append(cid)
            seen.add(cid)
        if duplicates:
            raise ValueError(
                f"Duplicate circuit_ids within drawing: {sorted(set(duplicates))}. "
                "Each circuit must have a unique ID."
            )
        return self


class HarnessDrawingUpdate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    revision: str | None = Field(default=None, min_length=5, max_length=5)
    title: str | None = Field(default=None, min_length=1, max_length=200)
    wire_ids: list[str] | None = None
    connector_ids: list[str] | None = None
    circuits: list[CircuitSchema] | None = None

    @field_validator("revision")
    @classmethod
    def validate_revision_format(cls, v: str | None) -> str | None:
        if v is not None and not _REVISION_PATTERN.match(v):
            raise ValueError(
                f"revision '{v}' is invalid. Must match Rev.[A-Z] (e.g. Rev.A, Rev.B)."
            )
        return v

    @model_validator(mode="after")
    def validate_circuit_ids_unique(self) -> "HarnessDrawingUpdate":
        if self.circuits is None:
            return self
        circuit_ids = [c.circuit_id for c in self.circuits]
        seen: set[str] = set()
        duplicates: list[str] = []
        for cid in circuit_ids:
            if cid in seen:
                duplicates.append(cid)
            seen.add(cid)
        if duplicates:
            raise ValueError(f"Duplicate circuit_ids within drawing: {sorted(set(duplicates))}.")
        return self


class HarnessDrawingResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: str = Field(description="MongoDB document id (mapped from _id)")
    drawing_id: str
    revision: str
    title: str
    wire_ids: list[str]
    connector_ids: list[str]
    circuits: list[CircuitSchema]


class ValidationReport(BaseModel):
    drawing_id: str
    valid: bool
    errors: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
