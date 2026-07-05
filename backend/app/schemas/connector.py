from pydantic import BaseModel, ConfigDict, Field

from app.models.connector import ConnectorGender, WaterproofStatus


class ConnectorCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    connector_id: str = Field(min_length=1, max_length=50)
    manufacturer: str = Field(min_length=1, max_length=100)
    pin_count: int = Field(gt=0, description="Number of pins; must be positive")
    housing_type: str = Field(min_length=1, max_length=50)
    gender: ConnectorGender
    waterproof_status: WaterproofStatus = WaterproofStatus.NOT_WATERPROOF
    mating_connector_id: str | None = Field(default=None, max_length=50)


class ConnectorUpdate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    manufacturer: str | None = Field(default=None, min_length=1, max_length=100)
    pin_count: int | None = Field(default=None, gt=0)
    housing_type: str | None = Field(default=None, min_length=1, max_length=50)
    gender: ConnectorGender | None = None
    waterproof_status: WaterproofStatus | None = None
    mating_connector_id: str | None = Field(default=None, max_length=50)


class ConnectorResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: str = Field(description="MongoDB document id (mapped from _id)")
    connector_id: str
    manufacturer: str
    pin_count: int
    housing_type: str
    gender: ConnectorGender
    waterproof_status: WaterproofStatus
    mating_connector_id: str | None = None
