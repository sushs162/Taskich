from pydantic import BaseModel, Field
from taskich.models import UserRole


class TaskCreateRequest(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: str = ""
    tags: list[str] = Field(default_factory=list)
    status: str = "todo"
    priority: str = "medium"
    assignee_id: int | None = None
    project_id: int | None = None


class TaskUpdateRequest(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = None
    tags: list[str] | None = None
    status: str | None = None
    priority: str | None = None
    assignee_id: int | None = None
    project_id: int | None = None


class ProjectCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=160)
    description: str = ""
    manager_id: int | None = None


class UserCreateRequest(BaseModel):
    username: str = Field(min_length=1, max_length=80)
    full_name: str = Field(min_length=1, max_length=160)
    role: UserRole = UserRole.USER


class FilterCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    query: str | None = None
    tags: list[str] = Field(default_factory=list)
    status: str | None = None
    priority: str | None = None
    assignee_id: int | None = None
    project_id: int | None = None
