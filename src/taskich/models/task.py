from dataclasses import dataclass, field

from taskich.models.constants import DEFAULT_PRIORITY, DEFAULT_STATUS


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
