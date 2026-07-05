from datetime import date

from pydantic import BaseModel, ConfigDict, Field


class MilestoneResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: str = Field(description="MongoDB document id")
    milestone_id: str
    title: str
    description: str
    achieved_at: date
