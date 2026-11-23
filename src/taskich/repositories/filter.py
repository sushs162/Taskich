from abc import ABC, abstractmethod
import logging
from sqlalchemy import select
from sqlalchemy.orm import Session
from taskich.database.orm_models import SavedFilterRecord
from taskich.models import SavedFilter
logger = logging.getLogger(__name__)

class FilterRepository(ABC):
    """Абстрактный контракт репозитория для соответствующей сущности."""

    @abstractmethod
    def save(self, saved_filter: SavedFilter) -> None:
        raise NotImplementedError

    @abstractmethod
    def get(self, name: str) -> SavedFilter | None:
        raise NotImplementedError

    @abstractmethod
    def delete(self, name: str) -> bool:
        raise NotImplementedError

    @abstractmethod
    def list_all(self) -> list[SavedFilter]:
        raise NotImplementedError

class InMemoryFilterRepository(FilterRepository):
    """Хранит фильтры в памяти во время работы программы."""

    def __init__(self) -> None:
        self._filters: dict[str, SavedFilter] = {}

    def save(self, saved_filter: SavedFilter) -> None:
        """Добавляет фильтр или заменяет существующий."""
        self._filters[saved_filter.name] = saved_filter
        logger.info("Сохранён фильтр '%s'", saved_filter.name)

    def get(self, name: str) -> SavedFilter | None:
        """Возвращает фильтр по его названию."""
        return self._filters.get(name)

    def delete(self, name: str) -> bool:
        """Удаляет фильтр и сообщает об успешном удалении."""
        if name not in self._filters:
            logger.warning("Попытка удалить несуществующий фильтр '%s'", name)
            return False
        del self._filters[name]
        logger.info("Удалён фильтр '%s'", name)
        return True

    def list_all(self) -> list[SavedFilter]:
        """Возвращает список всех сохранённых фильтров."""
        return list(self._filters.values())

class SqlAlchemyFilterRepository(FilterRepository):

    def __init__(self, session: Session):
        self.session = session

    @staticmethod
    def _domain(r: SavedFilterRecord) -> SavedFilter:
        return SavedFilter(r.name, r.query, list(r.tags or []), r.status, r.priority, r.assignee_id, r.project_id)

    def save(self, f: SavedFilter) -> None:
        r = self.session.get(SavedFilterRecord, f.name)
        if r is None:
            r = SavedFilterRecord(name=f.name)
            self.session.add(r)
        r.query, r.tags, r.status, r.priority, r.assignee_id, r.project_id = (f.query, f.tags, f.status, f.priority, f.assignee_id, f.project_id)

    def get(self, name: str) -> SavedFilter | None:
        r = self.session.get(SavedFilterRecord, name)
        return self._domain(r) if r else None

    def delete(self, name: str) -> bool:
        r = self.session.get(SavedFilterRecord, name)
        if not r:
            return False
        self.session.delete(r)
        return True

    def list_all(self) -> list[SavedFilter]:
        return [self._domain(r) for r in self.session.scalars(select(SavedFilterRecord).order_by(SavedFilterRecord.name))]
