from pydantic import BaseModel, ConfigDict
from taskich.models import UserRole


class TaskResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int; title: str; description: str; tags: list[str]; status: str; priority: str
    assignee_id: int | None; project_id: int | None


class ProjectResponse(BaseModel):
    id: int; name: str; description: str; manager_id: int | None


class UserResponse(BaseModel):
    id: int; username: str; full_name: str; role: UserRole


class FilterResponse(BaseModel):
    name: str; query: str | None; tags: list[str]; status: str | None
    priority: str | None; assignee_id: int | None; project_id: int | None


class MessageResponse(BaseModel):
    message: str
