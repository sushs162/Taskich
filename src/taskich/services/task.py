"""Service Layer: бизнес-операции над задачами."""

from taskich.database.unit_of_work import SqlAlchemyUnitOfWork
from taskich.models import Task
from taskich.patterns.strategies import (
    SearchStrategyType,
    get_search_strategy_factory,
)


class TaskService:
    """Содержит бизнес-операции над задачами."""

    def __init__(self, uow_factory=SqlAlchemyUnitOfWork) -> None:
        self.uow_factory = uow_factory

    def list_tasks(
        self,
        query: str | None = None,
        status: str | None = None,
        priority: str | None = None,
        project_id: int | None = None,
        assignee_id: int | None = None,
        tags: list[str] | None = None,
        strategy: SearchStrategyType = SearchStrategyType.TEXT,
    ) -> list[Task]:
        with self.uow_factory() as uow:
            tasks = uow.tasks.list_all()
            if query:
                search_strategy = get_search_strategy_factory(strategy).create_strategy()
                tasks = search_strategy.search(tasks, query)
            if status:
                tasks = [task for task in tasks if task.status.casefold() == status.casefold()]
            if priority:
                tasks = [
                    task for task in tasks
                    if task.priority.casefold() == priority.casefold()
                ]
            if project_id is not None:
                tasks = [task for task in tasks if task.project_id == project_id]
            if assignee_id is not None:
                tasks = [task for task in tasks if task.assignee_id == assignee_id]
            if tags:
                required_tags = {tag.casefold() for tag in tags}
                tasks = [
                    task for task in tasks
                    if required_tags.issubset({tag.casefold() for tag in task.tags})
                ]
            return tasks

    def apply_filter(self, name: str) -> list[Task] | None:
        with self.uow_factory() as uow:
            saved_filter = uow.filters.get(name)
        if saved_filter is None:
            return None
        return self.list_tasks(
            query=saved_filter.query,
            status=saved_filter.status,
            priority=saved_filter.priority,
            project_id=saved_filter.project_id,
            assignee_id=saved_filter.assignee_id,
            tags=saved_filter.tags,
        )

    def get_task(self, task_id: int) -> Task | None:
        with self.uow_factory() as uow:
            return uow.tasks.get(task_id)

    def create_task(
        self,
        *,
        title: str,
        description: str = "",
        tags: list[str] | None = None,
        status: str = "todo",
        priority: str = "medium",
        assignee_id: int | None = None,
        project_id: int | None = None,
    ) -> Task:
        with self.uow_factory() as uow:
            task = Task(
                uow.tasks.next_id(), title, description, tags or [], status,
                priority, assignee_id, project_id,
            )
            uow.tasks.add(task)
            uow.commit()
            return task

    def update_task(self, task_id: int, **changes) -> Task | None:
        with self.uow_factory() as uow:
            task = uow.tasks.get(task_id)
            if task is None:
                return None
            for key, value in changes.items():
                setattr(task, key, value)
            if not task.title or not uow.tasks.update(task):
                return None
            uow.commit()
            return task

    def delete_task(self, task_id: int) -> bool:
        with self.uow_factory() as uow:
            deleted = uow.tasks.delete(task_id)
            if deleted:
                uow.commit()
            return deleted
