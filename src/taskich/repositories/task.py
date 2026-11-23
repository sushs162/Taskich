from abc import ABC, abstractmethod
import logging
from sqlalchemy import select
from sqlalchemy.orm import Session
from taskich.database.orm_models import TaskRecord
from taskich.models import Task
logger = logging.getLogger(__name__)

class TaskRepository(ABC):
    """Абстрактный контракт репозитория для соответствующей сущности."""

    @abstractmethod
    def next_id(self) -> int:
        raise NotImplementedError

    @abstractmethod
    def add(self, task: Task) -> None:
        raise NotImplementedError

    @abstractmethod
    def get(self, task_id: int) -> Task | None:
        raise NotImplementedError

    @abstractmethod
    def update(self, task: Task) -> bool:
        raise NotImplementedError

    @abstractmethod
    def delete(self, task_id: int) -> bool:
        raise NotImplementedError

    @abstractmethod
    def list_all(self) -> list[Task]:
        raise NotImplementedError

    @abstractmethod
    def list_by_project(self, project_id: int) -> list[Task]:
        raise NotImplementedError

    @abstractmethod
    def list_by_assignee(self, user_id: int) -> list[Task]:
        raise NotImplementedError

class InMemoryTaskRepository(TaskRepository):
    """Хранит задачи в памяти во время работы программы."""

    def __init__(self) -> None:
        self._tasks: dict[int, Task] = {}

    def next_id(self) -> int:
        """Возвращает максимальный идентификатор плюс один."""
        return max(self._tasks, default=0) + 1

    def add(self, task: Task) -> None:
        """Добавляет задачу; повторный идентификатор считается ошибкой."""
        if task.id in self._tasks:
            raise ValueError(f'Задача с id={task.id} уже существует.')
        self._tasks[task.id] = task
        logger.info("Добавлена задача id=%s '%s'", task.id, task.title)

    def get(self, task_id: int) -> Task | None:
        """Возвращает задачу по идентификатору."""
        return self._tasks.get(task_id)

    def update(self, task: Task) -> bool:
        """Заменяет существующую задачу и сообщает, удалось ли это."""
        if task.id not in self._tasks:
            logger.warning('Попытка обновить несуществующую задачу id=%s', task.id)
            return False
        self._tasks[task.id] = task
        logger.info('Обновлена задача id=%s', task.id)
        return True

    def delete(self, task_id: int) -> bool:
        """Удаляет задачу и сообщает об успешном удалении."""
        if task_id not in self._tasks:
            logger.warning('Попытка удалить несуществующую задачу id=%s', task_id)
            return False
        del self._tasks[task_id]
        logger.info('Удалена задача id=%s', task_id)
        return True

    def list_all(self) -> list[Task]:
        """Возвращает список всех задач."""
        return list(self._tasks.values())

    def list_by_project(self, project_id: int) -> list[Task]:
        """Возвращает задачи указанного проекта."""
        return [t for t in self._tasks.values() if t.project_id == project_id]

    def list_by_assignee(self, user_id: int) -> list[Task]:
        """Возвращает задачи, назначенные указанному пользователю."""
        return [t for t in self._tasks.values() if t.assignee_id == user_id]

class SqlAlchemyTaskRepository(TaskRepository):

    def __init__(self, session: Session):
        self.session = session

    @staticmethod
    def _domain(r: TaskRecord) -> Task:
        return Task(r.id, r.title, r.description, list(r.tags or []), r.status, r.priority, r.assignee_id, r.project_id)

    def next_id(self) -> int:
        return (self.session.scalar(select(TaskRecord.id).order_by(TaskRecord.id.desc()).limit(1)) or 0) + 1

    def add(self, task: Task) -> None:
        self.session.add(TaskRecord(id=task.id, title=task.title, description=task.description, tags=task.tags, status=task.status, priority=task.priority, assignee_id=task.assignee_id, project_id=task.project_id))

    def get(self, task_id: int) -> Task | None:
        r = self.session.get(TaskRecord, task_id)
        return self._domain(r) if r else None

    def update(self, task: Task) -> bool:
        r = self.session.get(TaskRecord, task.id)
        if not r:
            return False
        r.title, r.description, r.tags, r.status, r.priority, r.assignee_id, r.project_id = (task.title, task.description, task.tags, task.status, task.priority, task.assignee_id, task.project_id)
        return True

    def delete(self, task_id: int) -> bool:
        r = self.session.get(TaskRecord, task_id)
        if not r:
            return False
        self.session.delete(r)
        return True

    def list_all(self) -> list[Task]:
        return [self._domain(r) for r in self.session.scalars(select(TaskRecord).order_by(TaskRecord.id))]

    def list_by_project(self, project_id: int) -> list[Task]:
        return [t for t in self.list_all() if t.project_id == project_id]

    def list_by_assignee(self, user_id: int) -> list[Task]:
        return [t for t in self.list_all() if t.assignee_id == user_id]
