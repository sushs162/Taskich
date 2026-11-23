from dataclasses import dataclass, field
from enum import StrEnum

DEFAULT_STATUS = "todo"
DEFAULT_PRIORITY = "medium"


class UserRole(StrEnum):
    """Роли пользователей системы."""

    ADMIN = "Admin"
    PROJECT_MANAGER = "Project Manager"
    USER = "User"


@dataclass
class User:
    """Представляет пользователя системы."""

    id: int
    username: str
    full_name: str
    role: UserRole = UserRole.USER

    @property
    def is_admin(self) -> bool:
        """Возвращает True, если пользователь — администратор."""

        return self.role is UserRole.ADMIN

    @property
    def can_manage_projects(self) -> bool:
        """Возвращает True, если пользователь может создавать проекты."""

        return self.role in (UserRole.ADMIN, UserRole.PROJECT_MANAGER)


@dataclass
class Project:
    """Представляет проект, в который объединяются задачи."""

    id: int
    name: str
    description: str = ""
    manager_id: int | None = None


@dataclass
class Task:
    """Представляет задачу с основными параметрами для поиска и фильтрации."""

    id: int
    title: str
    description: str
    tags: list[str] = field(default_factory=list)
    status: str = DEFAULT_STATUS
    priority: str = DEFAULT_PRIORITY
    assignee_id: int | None = None
    project_id: int | None = None


@dataclass
class SavedFilter:
    """Представляет сохранённый пользователем набор параметров поиска."""

    name: str
    query: str | None = None
    tags: list[str] = field(default_factory=list)
    status: str | None = None
    priority: str | None = None
    assignee_id: int | None = None
    project_id: int | None = None
