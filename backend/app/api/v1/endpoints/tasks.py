from fastapi import APIRouter, Response

from app.core.types import Priority
from app.models.task import TaskModel
from app.schemas.task import TaskCreate, TaskResponse, TaskUpdate
from app.services.task_service import TaskService

router = APIRouter(prefix="/tasks", tags=["tasks"])


def _to_response(task: TaskModel) -> TaskResponse:
    return TaskResponse(
        id=task.mongo_id or "",
        task_id=task.task_id,
        title=task.title,
        priority=task.priority,
        is_done=task.is_done,
        due_date=task.due_date,
        due_time=task.due_time,
        category_id=task.category_id,
        notes=task.notes,
        completed_at=task.completed_at,
        created_at=task.created_at,
    )


@router.get("", response_model=list[TaskResponse])
async def list_tasks(
    date: str | None = None,
    category_id: str | None = None,
    done: bool | None = None,
    priority: Priority | None = None,
) -> list[TaskResponse]:
    tasks = await TaskService().list_tasks(
        date=date, category_id=category_id, is_done=done, priority=priority
    )
    return [_to_response(t) for t in tasks]


@router.post("", response_model=TaskResponse, status_code=201)
async def create_task(body: TaskCreate) -> TaskResponse:
    task = await TaskService().create_task(body.model_dump(exclude_none=True))
    return _to_response(task)


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(task_id: str) -> TaskResponse:
    task = await TaskService().get_task(task_id)
    return _to_response(task)


@router.put("/{task_id}", response_model=TaskResponse)
async def update_task(task_id: str, body: TaskUpdate) -> TaskResponse:
    task = await TaskService().update_task(task_id, body.model_dump(exclude_unset=True))
    return _to_response(task)


@router.delete("/{task_id}", status_code=204)
async def delete_task(task_id: str) -> Response:
    await TaskService().delete_task(task_id)
    return Response(status_code=204)


@router.patch("/{task_id}/done", response_model=TaskResponse)
async def toggle_done(task_id: str) -> TaskResponse:
    task = await TaskService().toggle_done(task_id)
    return _to_response(task)
