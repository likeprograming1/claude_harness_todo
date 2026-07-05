from dataclasses import dataclass, field
from datetime import datetime

from app.core.types import Priority


@dataclass
class TaskModel:
    task_id: str
    title: str
    priority: Priority = Priority.MEDIUM
    is_done: bool = False
    due_date: str | None = None       # YYYY-MM-DD
    due_time: str | None = None       # HH:MM
    category_id: str | None = None
    notes: str | None = None
    completed_at: datetime | None = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    mongo_id: str | None = None
