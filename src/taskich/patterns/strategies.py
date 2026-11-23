"""GoF Strategy и Factory Method для поиска задач."""
from abc import ABC, abstractmethod
from collections.abc import Sequence
from typing import Protocol
from taskich.models import Task


class SearchStrategy(Protocol):
    def search(self, tasks: Sequence[Task], query: str) -> list[Task]: ...


class TextSearchStrategy:
    """Поиск подстроки в названии, описании и тегах."""
    def search(self, tasks: Sequence[Task], query: str) -> list[Task]:
        q = query.strip().casefold()
        if not q: return list(tasks)
        return [t for t in tasks if any(q in field.casefold() for field in [t.title, t.description, *t.tags])]


class TagSearchStrategy:
    """Поиск задач по точному совпадению тега."""
    def search(self, tasks: Sequence[Task], query: str) -> list[Task]:
        q = query.strip().casefold()
        if not q: return list(tasks)
        return [t for t in tasks if any(tag.casefold() == q for tag in t.tags)]


class SearchStrategyFactory(ABC):
    """Creator из Factory Method: объявляет фабричный метод создания стратегии."""
    @abstractmethod
    def create_strategy(self) -> SearchStrategy:
        raise NotImplementedError


class TextSearchFactory(SearchStrategyFactory):
    def create_strategy(self) -> SearchStrategy:
        return TextSearchStrategy()


class TagSearchFactory(SearchStrategyFactory):
    def create_strategy(self) -> SearchStrategy:
        return TagSearchStrategy()


def get_search_strategy_factory(name: str) -> SearchStrategyFactory:
    """Возвращает конкретную фабрику; создание продукта делегируется Factory Method."""
    factories: dict[str, type[SearchStrategyFactory]] = {
        "text": TextSearchFactory,
        "tag": TagSearchFactory,
    }
    try:
        return factories[name.casefold()]()
    except KeyError as exc:
        raise ValueError(f"Неизвестная стратегия поиска: {name}") from exc
