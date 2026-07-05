import re
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.core.types import Priority

_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
_TIME_RE = re.compile(r"^\d{2}:\d{2}$")


class TaskCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    task_id: str | None = Field(default=None, max_length=50)
    title: str = Field(min_length=1, max_length=200)
    due_date: str | None = Field(default=None, description="YYYY-MM-DD")
    due_time: str | None = Field(default=None, description="HH:MM")
    category_id: str | None = Field(default=None, max_length=50)
    priority: Priority = Priority.MEDIUM
    notes: str | None = Field(default=None, max_length=1000)

    @field_validator("due_date")
    @classmethod
    def validate_due_date(cls, v: str | None) -> str | None:
        if v is not None and not _DATE_RE.match(v):
            raise ValueError("due_date must be YYYY-MM-DD format")
        return v

    @field_validator("due_time")
    @classmethod
    def validate_due_time(cls, v: str | None) -> str | None:
        if v is not None and not _TIME_RE.match(v):
            raise ValueError("due_time must be HH:MM format")
        return v

    @model_validator(mode="after")
    def due_time_requires_due_date(self) -> "TaskCreate":
        if self.due_time is not None and self.due_date is None:
            raise ValueError("due_time requires due_date to be set")
        return self


class TaskUpdate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    title: str | None = Field(default=None, min_length=1, max_length=200)
    due_date: str | None = Field(default=None)
    due_time: str | None = Field(default=None)
    category_id: str | None = Field(default=None, max_length=50)
    priority: Priority | None = None
    notes: str | None = Field(default=None, max_length=1000)

    @field_validator("due_date")
    @classmethod
    def validate_due_date(cls, v: str | None) -> str | None:
        if v is not None and not _DATE_RE.match(v):
            raise ValueError("due_date must be YYYY-MM-DD format")
        return v

    @field_validator("due_time")
    @classmethod
    def validate_due_time(cls, v: str | None) -> str | None:
        if v is not None and not _TIME_RE.match(v):
            raise ValueError("due_time must be HH:MM format")
        return v


class TaskResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: str = Field(description="MongoDB document id")
    task_id: str
    title: str
    priority: Priority
    is_done: bool
    due_date: str | None
    due_time: str | None
    category_id: str | None
    notes: str | None
    completed_at: datetime | None
    created_at: datetime
