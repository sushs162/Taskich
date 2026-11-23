from dataclasses import dataclass, field


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
