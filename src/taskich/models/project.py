from dataclasses import dataclass


@dataclass
class Project:
    """Представляет проект, в который объединяются задачи."""

    id: int
    name: str
    description: str = ""
    manager_id: int | None = None
