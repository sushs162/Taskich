import logging
from collections.abc import Sequence

from taskich.models import SavedFilter, Task

logger = logging.getLogger(__name__)


def search_tasks(tasks: Sequence[Task], query: str) -> list[Task]:
    """Ищет задачи по названию, описанию и тегам."""

    normalized_query = query.strip().lower()

    if not normalized_query:
        return list(tasks)

    result: list[Task] = []

    for task in tasks:
        # Ищем в каждом поле отдельно, чтобы запрос не "склеивался"
        # из конца названия и начала описания.
        fields = [task.title, task.description, *task.tags]

        if any(normalized_query in field.lower() for field in fields):
            result.append(task)

    logger.debug("Поиск '%s': найдено %s задач", normalized_query, len(result))
    return result


def filter_tasks(
    tasks: Sequence[Task],
    *,
    tags: list[str] | None = None,
    status: str | None = None,
    priority: str | None = None,
    assignee_id: int | None = None,
    project_id: int | None = None,
) -> list[Task]:
    """Фильтрует задачи по тегам, статусу, приоритету, исполнителю и проекту."""

    result = list(tasks)

    if tags:
        required_tags = {tag.strip().lower() for tag in tags if tag.strip()}

        result = [
            task
            for task in result
            if required_tags.issubset({tag.lower() for tag in task.tags})
        ]

    if status:
        normalized_status = status.strip().lower()
        result = [task for task in result if task.status.lower() == normalized_status]

    if priority:
        normalized_priority = priority.strip().lower()
        result = [
            task for task in result if task.priority.lower() == normalized_priority
        ]

    if assignee_id is not None:
        result = [task for task in result if task.assignee_id == assignee_id]

    if project_id is not None:
        result = [task for task in result if task.project_id == project_id]

    logger.debug("Фильтрация: %s из %s задач", len(result), len(tasks))
    return result


def search_and_filter_tasks(
    tasks: Sequence[Task],
    *,
    query: str | None = None,
    tags: list[str] | None = None,
    status: str | None = None,
    priority: str | None = None,
    assignee_id: int | None = None,
    project_id: int | None = None,
) -> list[Task]:
    """Выполняет поиск и затем применяет выбранные фильтры."""

    result = list(tasks)

    if query:
        result = search_tasks(result, query)

    return filter_tasks(
        result,
        tags=tags,
        status=status,
        priority=priority,
        assignee_id=assignee_id,
        project_id=project_id,
    )


def apply_saved_filter(
    tasks: Sequence[Task],
    saved_filter: SavedFilter,
) -> list[Task]:
    """Применяет сохранённый пользователем фильтр к списку задач."""

    return search_and_filter_tasks(
        tasks,
        query=saved_filter.query,
        tags=saved_filter.tags,
        status=saved_filter.status,
        priority=saved_filter.priority,
        assignee_id=saved_filter.assignee_id,
        project_id=saved_filter.project_id,
    )
