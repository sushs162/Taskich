from fastapi import APIRouter, Depends, HTTPException
from taskich.api.dependencies import get_catalog_service, get_task_service
from taskich.dtos.requests import ProjectCreateRequest, UserCreateRequest, FilterCreateRequest
from taskich.dtos.responses import ProjectResponse, UserResponse, FilterResponse, MessageResponse, TaskResponse
from taskich.models import SavedFilter
from taskich.services.catalog_service import CatalogService
from taskich.services.task_service import TaskService

router = APIRouter(prefix="/api", tags=["Справочники"])


@router.get("/projects", response_model=list[ProjectResponse])
def list_projects(service: CatalogService = Depends(get_catalog_service)): return service.list_projects()


@router.post("/projects", response_model=ProjectResponse, status_code=201)
def create_project(data: ProjectCreateRequest, service: CatalogService = Depends(get_catalog_service)): return service.create_project(**data.model_dump())


@router.get("/users", response_model=list[UserResponse])
def list_users(service: CatalogService = Depends(get_catalog_service)): return service.list_users()


@router.post("/users", response_model=UserResponse, status_code=201)
def create_user(data: UserCreateRequest, service: CatalogService = Depends(get_catalog_service)):
    try: return service.create_user(**data.model_dump())
    except ValueError as exc: raise HTTPException(409, str(exc)) from exc


@router.get("/filters", response_model=list[FilterResponse])
def list_filters(service: CatalogService = Depends(get_catalog_service)): return service.list_filters()


@router.post("/filters", response_model=FilterResponse, status_code=201)
def save_filter(data: FilterCreateRequest, service: CatalogService = Depends(get_catalog_service)):
    return service.save_filter(SavedFilter(**data.model_dump()))


@router.delete("/filters/{name}", response_model=MessageResponse)
def delete_filter(name: str, service: CatalogService = Depends(get_catalog_service)):
    if not service.delete_filter(name): raise HTTPException(404, "Фильтр не найден")
    return {"message": "Фильтр удалён"}


@router.get("/filters/{name}/tasks", response_model=list[TaskResponse])
def apply_filter(name: str, service: TaskService = Depends(get_task_service)):
    tasks = service.apply_filter(name)
    if tasks is None: raise HTTPException(404, "Фильтр не найден")
    return tasks
