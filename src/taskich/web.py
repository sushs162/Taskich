from contextlib import asynccontextmanager
from pathlib import Path
from typing import Annotated

from fastapi import Depends, FastAPI, Form, Request
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from taskich.api.dependencies import get_catalog_service, get_task_service
from taskich.api.routers import catalog, tasks
from taskich.bootstrap import initialize_application
from taskich.services.catalog import CatalogService
from taskich.services.task import TaskService

BASE_DIR = Path(__file__).resolve().parent


@asynccontextmanager
async def lifespan(application: FastAPI):
    initialize_application()
    yield


app = FastAPI(
    title="Taskich",
    description="Простой менеджер задач и проектов",
    lifespan=lifespan,
)
app.include_router(tasks.router)
app.include_router(catalog.router)
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
templates = Jinja2Templates(directory=BASE_DIR / "templates")


@app.get("/", name="home")
def home(
    request: Request,
    service: Annotated[TaskService, Depends(get_task_service)],
    catalog_service: Annotated[CatalogService, Depends(get_catalog_service)],
    query: str = "",
    status: str = "",
):
    task_list = service.list_tasks(query=query or None, status=status or None)
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "tasks": task_list,
            "projects": catalog_service.list_projects(),
            "query": query,
            "status": status,
        },
    )


@app.post("/tasks", name="ui_create_task")
def ui_create_task(
    service: Annotated[TaskService, Depends(get_task_service)],
    title: str = Form(...),
    description: str = Form(""),
    priority: str = Form("medium"),
    project_id: int | None = Form(None),
):
    service.create_task(
        title=title,
        description=description,
        priority=priority,
        project_id=project_id,
    )
    return RedirectResponse(url="/", status_code=303)


@app.post("/tasks/{task_id}/delete", name="ui_delete_task")
def ui_delete_task(
    task_id: int,
    service: Annotated[TaskService, Depends(get_task_service)],
):
    service.delete_task(task_id)
    return RedirectResponse(url="/", status_code=303)
