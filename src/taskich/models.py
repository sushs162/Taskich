from dataclasses import dataclass, field


@dataclass
class Task:
    """Представляет задачу с основными параметрами для поиска и фильтрации."""

    id: int
    title: str
    description: str
    tags: list[str] = field(default_factory=list)
    status: str = "todo"
    priority: str = "medium"
    assignee: str | None = None


@dataclass
class SavedFilter:
    """Представляет сохранённый пользователем набор параметров поиска."""

    name: str
    query: str | None = None
    tags: list[str] = field(default_factory=list)
    status: str | None = None
    priority: str | None = None
    assignee: str | None = None
