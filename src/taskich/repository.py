import logging

from taskich.models import Project, SavedFilter, Task, User
from taskich.repositories.interfaces import (
    FilterRepository,
    ProjectRepository,
    TaskRepository,
    UserRepository,
)

logger = logging.getLogger(__name__)


class InMemoryFilterRepository:
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


class InMemoryTaskRepository:
    """Хранит задачи в памяти во время работы программы."""

    def __init__(self) -> None:
        self._tasks: dict[int, Task] = {}

    def next_id(self) -> int:
        """Возвращает максимальный идентификатор плюс один."""

        return max(self._tasks, default=0) + 1

    def add(self, task: Task) -> None:
        """Добавляет задачу; повторный идентификатор считается ошибкой."""

        if task.id in self._tasks:
            raise ValueError(f"Задача с id={task.id} уже существует.")

        self._tasks[task.id] = task
        logger.info("Добавлена задача id=%s '%s'", task.id, task.title)

    def get(self, task_id: int) -> Task | None:
        """Возвращает задачу по идентификатору."""

        return self._tasks.get(task_id)

    def update(self, task: Task) -> bool:
        """Заменяет существующую задачу и сообщает, удалось ли это."""

        if task.id not in self._tasks:
            logger.warning("Попытка обновить несуществующую задачу id=%s", task.id)
            return False

        self._tasks[task.id] = task
        logger.info("Обновлена задача id=%s", task.id)
        return True

    def delete(self, task_id: int) -> bool:
        """Удаляет задачу и сообщает об успешном удалении."""

        if task_id not in self._tasks:
            logger.warning("Попытка удалить несуществующую задачу id=%s", task_id)
            return False

        del self._tasks[task_id]
        logger.info("Удалена задача id=%s", task_id)
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


class InMemoryUserRepository:
    """Хранит пользователей в памяти во время работы программы."""

    def __init__(self) -> None:
        self._users: dict[int, User] = {}

    def next_id(self) -> int:
        """Возвращает максимальный идентификатор плюс один."""

        return max(self._users, default=0) + 1

    def add(self, user: User) -> None:
        """Добавляет пользователя; id и логин должны быть уникальными."""

        if user.id in self._users:
            raise ValueError(f"Пользователь с id={user.id} уже существует.")

        if self.get_by_username(user.username) is not None:
            raise ValueError(f"Логин '{user.username}' уже занят.")

        self._users[user.id] = user
        logger.info("Добавлен пользователь id=%s '%s' (%s)", user.id, user.username, user.role)

    def get(self, user_id: int) -> User | None:
        """Возвращает пользователя по идентификатору."""

        return self._users.get(user_id)

    def get_by_username(self, username: str) -> User | None:
        """Возвращает пользователя по логину без учёта регистра."""

        normalized = username.strip().lower()

        for user in self._users.values():
            if user.username.lower() == normalized:
                return user

        return None

    def delete(self, user_id: int) -> bool:
        """Удаляет пользователя и сообщает об успешном удалении."""

        if user_id not in self._users:
            logger.warning("Попытка удалить несуществующего пользователя id=%s", user_id)
            return False

        del self._users[user_id]
        logger.info("Удалён пользователь id=%s", user_id)
        return True

    def list_all(self) -> list[User]:
        """Возвращает список всех пользователей."""

        return list(self._users.values())


class InMemoryProjectRepository:
    """Хранит проекты в памяти во время работы программы."""

    def __init__(self) -> None:
        self._projects: dict[int, Project] = {}

    def next_id(self) -> int:
        """Возвращает максимальный идентификатор плюс один."""

        return max(self._projects, default=0) + 1

    def add(self, project: Project) -> None:
        """Добавляет проект; повторный идентификатор считается ошибкой."""

        if project.id in self._projects:
            raise ValueError(f"Проект с id={project.id} уже существует.")

        self._projects[project.id] = project
        logger.info("Добавлен проект id=%s '%s'", project.id, project.name)

    def get(self, project_id: int) -> Project | None:
        """Возвращает проект по идентификатору."""

        return self._projects.get(project_id)

    def delete(self, project_id: int) -> bool:
        """Удаляет проект и сообщает об успешном удалении."""

        if project_id not in self._projects:
            logger.warning("Попытка удалить несуществующий проект id=%s", project_id)
            return False

        del self._projects[project_id]
        logger.info("Удалён проект id=%s", project_id)
        return True

    def list_all(self) -> list[Project]:
        """Возвращает список всех проектов."""

        return list(self._projects.values())
