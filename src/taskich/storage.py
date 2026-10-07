from typing import Protocol

from taskich.models import SavedFilter


class FilterRepository(Protocol):
    """Определяет операции, необходимые для работы с сохранёнными фильтрами."""

    def save(self, saved_filter: SavedFilter) -> None:
        """Сохраняет фильтр."""

    def get(self, name: str) -> SavedFilter | None:
        """Возвращает фильтр по имени."""

    def delete(self, name: str) -> bool:
        """Удаляет фильтр по имени."""

    def list_all(self) -> list[SavedFilter]:
        """Возвращает все сохранённые фильтры."""


class InMemoryFilterRepository:
    """Хранит фильтры в памяти во время работы программы."""

    def __init__(self) -> None:
        self._filters: dict[str, SavedFilter] = {}

    def save(self, saved_filter: SavedFilter) -> None:
        """Добавляет фильтр или заменяет существующий."""

        self._filters[saved_filter.name] = saved_filter

    def get(self, name: str) -> SavedFilter | None:
        """Возвращает фильтр по его названию."""

        return self._filters.get(name)

    def delete(self, name: str) -> bool:
        """Удаляет фильтр и сообщает об успешном удалении."""

        if name not in self._filters:
            return False

        del self._filters[name]
        return True

    def list_all(self) -> list[SavedFilter]:
        """Возвращает список всех сохранённых фильтров."""

        return list(self._filters.values())
