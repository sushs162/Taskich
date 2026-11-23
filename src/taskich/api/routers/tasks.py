from fastapi import APIRouter, Depends, HTTPException, Query
from taskich.api.dependencies import get_task_service
from taskich.dtos.requests import TaskCreateRequest, TaskUpdateRequest
from taskich.dtos.responses import TaskResponse, MessageResponse
from taskich.services.task_service import TaskService

router = APIRouter(prefix="/api/tasks", tags=["Задачи"])


@router.get("", response_model=list[TaskResponse])
def list_tasks(query: str | None = None, status: str | None = None, priority: str | None = None, project_id: int | None = None, assignee_id: int | None = None, tags: list[str] | None = Query(None), strategy: str = Query("text", pattern="^(text|tag)$"), service: TaskService = Depends(get_task_service)):
    return service.list_tasks(query, status, priority, project_id, assignee_id, tags, strategy)


@router.get("/{task_id}", response_model=TaskResponse)
def get_task(task_id: int, service: TaskService = Depends(get_task_service)):
    task = service.get_task(task_id)
    if task is None: raise HTTPException(404, "Задача не найдена")
    return task


@router.post("", response_model=TaskResponse, status_code=201)
def create_task(data: TaskCreateRequest, service: TaskService = Depends(get_task_service)):
    return service.create_task(**data.model_dump())


@router.patch("/{task_id}", response_model=TaskResponse)
def update_task(task_id: int, data: TaskUpdateRequest, service: TaskService = Depends(get_task_service)):
    task = service.update_task(task_id, **data.model_dump(exclude_unset=True))
    if task is None: raise HTTPException(404, "Задача не найдена")
    return task


@router.delete("/{task_id}", response_model=MessageResponse)
def delete_task(task_id: int, service: TaskService = Depends(get_task_service)):
    if not service.delete_task(task_id): raise HTTPException(404, "Задача не найдена")
    return {"message": "Задача удалена"}
