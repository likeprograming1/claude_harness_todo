from app.core.exceptions import AppValidationError, EntityNotFoundError
from app.core.types import Priority
from app.models.task import TaskModel
from app.repositories.category_repository import CategoryRepository
from app.repositories.task_repository import TaskRepository
from app.services.milestone_service import MilestoneService


class TaskService:
    def __init__(
        self,
        task_repo: TaskRepository | None = None,
        category_repo: CategoryRepository | None = None,
        milestone_svc: MilestoneService | None = None,
    ) -> None:
        self._task_repo = task_repo or TaskRepository()
        self._category_repo = category_repo or CategoryRepository()
        self._milestone_svc = milestone_svc or MilestoneService()

    async def list_tasks(
        self,
        *,
        date: str | None = None,
        category_id: str | None = None,
        is_done: bool | None = None,
        priority: Priority | None = None,
    ) -> list[TaskModel]:
        return await self._task_repo.list_all(
            date=date,
            category_id=category_id,
            is_done=is_done,
            priority=priority,
        )

    async def get_task(self, task_id: str) -> TaskModel:
        task = await self._task_repo.get_by_id(task_id)
        if task is None:
            raise EntityNotFoundError("Task", task_id)
        return task

    async def create_task(self, data: dict[str, object]) -> TaskModel:
        cat_id = data.get("category_id")
        if cat_id and not await self._category_repo.exists(str(cat_id)):
            raise AppValidationError([f"category_id '{cat_id}' does not exist"])
        return await self._task_repo.create(data)

    async def update_task(self, task_id: str, data: dict[str, object]) -> TaskModel:
        existing = await self._task_repo.get_by_id(task_id)
        if existing is None:
            raise EntityNotFoundError("Task", task_id)

        cat_id = data.get("category_id")
        if cat_id is not None and not await self._category_repo.exists(str(cat_id)):
            raise AppValidationError([f"category_id '{cat_id}' does not exist"])

        # due_time requires due_date in the effective state after the update
        effective_due_date = data.get("due_date", existing.due_date)
        effective_due_time = data.get("due_time", existing.due_time)
        if effective_due_time is not None and effective_due_date is None:
            raise AppValidationError(["due_time requires due_date to be set"])

        updated = await self._task_repo.update(task_id, data)
        if updated is None:
            raise EntityNotFoundError("Task", task_id)
        return updated

    async def delete_task(self, task_id: str) -> None:
        deleted = await self._task_repo.delete(task_id)
        if not deleted:
            raise EntityNotFoundError("Task", task_id)

    async def toggle_done(self, task_id: str) -> TaskModel:
        task = await self._task_repo.toggle_done(task_id)
        if task is None:
            raise EntityNotFoundError("Task", task_id)
        if task.is_done:
            await self._milestone_svc.check_and_grant()
        return task
