from dataclasses import dataclass
from enum import StrEnum


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
        return self.role is UserRole.ADMIN

    @property
    def can_manage_projects(self) -> bool:
        return self.role in (UserRole.ADMIN, UserRole.PROJECT_MANAGER)
