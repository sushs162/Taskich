"""GoF Strategy и Factory Method для поиска задач."""

from abc import ABC, abstractmethod
from collections.abc import Sequence
from enum import StrEnum
from typing import Protocol

from taskich.models import Task


class SearchStrategyType(StrEnum):
    """Поддерживаемые способы поиска задач."""

    TEXT = "text"
    TAG = "tag"


class SearchStrategy(Protocol):
    def search(self, tasks: Sequence[Task], query: str) -> list[Task]: ...


class TextSearchStrategy:
    """Поиск подстроки в названии, описании и тегах."""

    def search(self, tasks: Sequence[Task], query: str) -> list[Task]:
        normalized_query = query.strip().casefold()
        if not normalized_query:
            return list(tasks)
        return [
            task
            for task in tasks
            if any(
                normalized_query in field.casefold()
                for field in [task.title, task.description, *task.tags]
            )
        ]


class TagSearchStrategy:
    """Поиск задач по точному совпадению тега."""

    def search(self, tasks: Sequence[Task], query: str) -> list[Task]:
        normalized_query = query.strip().casefold()
        if not normalized_query:
            return list(tasks)
        return [
            task
            for task in tasks
            if any(tag.casefold() == normalized_query for tag in task.tags)
        ]


class SearchStrategyFactory(ABC):
    """Creator из Factory Method: объявляет фабричный метод стратегии."""

    @abstractmethod
    def create_strategy(self) -> SearchStrategy:
        raise NotImplementedError


class TextSearchFactory(SearchStrategyFactory):
    def create_strategy(self) -> SearchStrategy:
        return TextSearchStrategy()


class TagSearchFactory(SearchStrategyFactory):
    def create_strategy(self) -> SearchStrategy:
        return TagSearchStrategy()


def get_search_strategy_factory(
    strategy_type: SearchStrategyType | str,
) -> SearchStrategyFactory:
    """Возвращает фабрику выбранной стратегии поиска."""
    normalized_type = SearchStrategyType(strategy_type)
    factories: dict[SearchStrategyType, type[SearchStrategyFactory]] = {
        SearchStrategyType.TEXT: TextSearchFactory,
        SearchStrategyType.TAG: TagSearchFactory,
    }
    return factories[normalized_type]()
