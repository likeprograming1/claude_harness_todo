from dataclasses import dataclass
from datetime import date


@dataclass
class MilestoneModel:
    milestone_id: str
    title: str
    description: str
    achieved_at: date
    mongo_id: str | None = None
