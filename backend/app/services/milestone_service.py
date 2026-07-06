from datetime import date, timedelta

from app.models.milestone import MilestoneModel
from app.repositories.milestone_repository import MilestoneRepository
from app.repositories.task_repository import TaskRepository

_MILESTONE_META: dict[str, tuple[str, str]] = {
    "total_10": ("10개 완료!", "할 일을 10개 완료했습니다"),
    "total_50": ("50개 완료!", "할 일을 50개 완료했습니다"),
    "streak_3": ("3일 연속!", "3일 연속으로 할 일을 완료했습니다"),
    "streak_7": ("7일 연속!", "7일 연속으로 할 일을 완료했습니다"),
    "focus_5":  ("집중의 달인", "하루에 집중 할 일을 5개 이상 완료했습니다"),
}


class MilestoneService:
    def __init__(
        self,
        milestone_repo: MilestoneRepository | None = None,
        task_repo: TaskRepository | None = None,
    ) -> None:
        self._milestone_repo = milestone_repo or MilestoneRepository()
        self._task_repo = task_repo or TaskRepository()

    async def list_milestones(self) -> list[MilestoneModel]:
        return await self._milestone_repo.list_all()

    async def check_and_grant(self) -> list[MilestoneModel]:
        newly_granted: list[MilestoneModel] = []

        total = await self._task_repo.count_total_completed()
        for mid, threshold in [("total_10", 10), ("total_50", 50)]:
            if total >= threshold and not await self._milestone_repo.exists(mid):
                m = await self._milestone_repo.create(
                    self._build_payload(mid, date.today())
                )
                newly_granted.append(m)

        streak = await self._compute_streak()
        for mid, required in [("streak_7", 7), ("streak_3", 3)]:
            if streak >= required and not await self._milestone_repo.exists(mid):
                m = await self._milestone_repo.create(
                    self._build_payload(mid, date.today())
                )
                newly_granted.append(m)

        today_str = date.today().isoformat()
        focus_tasks = await self._task_repo.list_all(
            date=today_str, category_id="cat_focus", is_done=True
        )
        if len(focus_tasks) >= 5 and not await self._milestone_repo.exists("focus_5"):
            m = await self._milestone_repo.create(
                self._build_payload("focus_5", date.today())
            )
            newly_granted.append(m)

        return newly_granted

    async def _compute_streak(self) -> int:
        today = date.today()
        start = (today - timedelta(days=6)).isoformat()
        end = today.isoformat()
        tasks = await self._task_repo.get_by_due_date_range(start, end)
        completed_dates = {t.due_date for t in tasks if t.is_done and t.due_date}
        streak = 0
        check_date = today
        while check_date.isoformat() in completed_dates:
            streak += 1
            check_date -= timedelta(days=1)
        return streak

    @staticmethod
    def _build_payload(mid: str, achieved_at: date) -> dict[str, object]:
        title, description = _MILESTONE_META[mid]
        return {
            "milestone_id": mid,
            "title": title,
            "description": description,
            "achieved_at": achieved_at,
        }
