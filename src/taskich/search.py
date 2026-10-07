from collections.abc import Sequence

from taskich.models import SavedFilter, Task


def search_tasks(tasks: Sequence[Task], query: str) -> list[Task]:
    """Ищет задачи по названию, описанию и тегам."""

    normalized_query = query.strip().lower()

    if not normalized_query:
        return list(tasks)

    result: list[Task] = []

    for task in tasks:
        searchable_text = " ".join(
            [
                task.title,
                task.description,
                *task.tags,
            ]
        ).lower()

        if normalized_query in searchable_text:
            result.append(task)

    return result


def filter_tasks(
    tasks: Sequence[Task],
    *,
    tags: list[str] | None = None,
    status: str | None = None,
    priority: str | None = None,
    assignee: str | None = None,
) -> list[Task]:
    """Фильтрует задачи по тегам, статусу, приоритету и исполнителю."""

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

    if assignee:
        normalized_assignee = assignee.strip().lower()
        result = [
            task
            for task in result
            if task.assignee is not None
            and task.assignee.lower() == normalized_assignee
        ]

    return result


def search_and_filter_tasks(
    tasks: Sequence[Task],
    *,
    query: str | None = None,
    tags: list[str] | None = None,
    status: str | None = None,
    priority: str | None = None,
    assignee: str | None = None,
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
        assignee=assignee,
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
        assignee=saved_filter.assignee,
    )
