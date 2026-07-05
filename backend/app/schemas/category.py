import re

from pydantic import BaseModel, ConfigDict, Field, field_validator

_HEX_RE = re.compile(r"^#[0-9A-Fa-f]{6}$")


class CategoryCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    name: str = Field(min_length=1, max_length=50)
    color: str = Field(default="#888888", max_length=7)

    @field_validator("color")
    @classmethod
    def validate_color(cls, v: str) -> str:
        if not _HEX_RE.match(v):
            raise ValueError("color must be a valid hex code (#RRGGBB)")
        return v


class CategoryResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: str = Field(description="MongoDB document id")
    category_id: str
    name: str
    color: str
    is_default: bool
