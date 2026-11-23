import logging
from collections.abc import Callable
from enum import IntEnum
from typing import Any, TypeVar

from taskich.models import (
    DEFAULT_PRIORITY,
    DEFAULT_STATUS,
    Project,
    SavedFilter,
    Task,
    User,
    UserRole,
)
from taskich.repository import (
    FilterRepository,
    ProjectRepository,
    TaskRepository,
    UserRepository,
)
from taskich.search import (
    apply_saved_filter,
    filter_tasks,
    search_and_filter_tasks,
    search_tasks,
)

logger = logging.getLogger(__name__)


class MenuChoice(IntEnum):
    """Пункты главного меню; значение — число, которое вводит пользователь."""

    EXIT = 0
    SEARCH = 1
    FILTER = 2
    SEARCH_AND_FILTER = 3
    SAVE_FILTER = 4
    SHOW_FILTERS = 5
    DELETE_FILTER = 6
    SHOW_TASKS = 7
    CREATE_TASK = 8
    SHOW_PROJECTS = 9
    CREATE_PROJECT = 10
    SHOW_USERS = 11
    CREATE_USER = 12


class RoleChoice(IntEnum):
    """Варианты выбора роли при создании пользователя."""

    ADMIN = 1
    PROJECT_MANAGER = 2
    USER = 3


MENU_TITLES: dict[MenuChoice, str] = {
    MenuChoice.SEARCH: "Поиск задач",
    MenuChoice.FILTER: "Фильтрация задач",
    MenuChoice.SEARCH_AND_FILTER: "Поиск + фильтрация",
    MenuChoice.SAVE_FILTER: "Сохранить фильтр",
    MenuChoice.SHOW_FILTERS: "Сохранённые фильтры",
    MenuChoice.DELETE_FILTER: "Удалить фильтр",
    MenuChoice.SHOW_TASKS: "Все задачи",
    MenuChoice.CREATE_TASK: "Создать задачу",
    MenuChoice.SHOW_PROJECTS: "Проекты",
    MenuChoice.CREATE_PROJECT: "Создать проект (Admin, Project Manager)",
    MenuChoice.SHOW_USERS: "Пользователи",
    MenuChoice.CREATE_USER: "Создать пользователя (Admin)",
    MenuChoice.EXIT: "Выход",
}

ROLE_BY_CHOICE: dict[RoleChoice, UserRole] = {
    RoleChoice.ADMIN: UserRole.ADMIN,
    RoleChoice.PROJECT_MANAGER: UserRole.PROJECT_MANAGER,
    RoleChoice.USER: UserRole.USER,
}

ChoiceT = TypeVar("ChoiceT", bound=IntEnum)


class CLIError(Exception):
    """Ошибка ввода или нехватка прав; текст ошибки показывается пользователю."""


class TaskichCLI:
    """Интерактивное консольное меню Taskich."""

    def __init__(
        self,
        tasks: TaskRepository,
        users: UserRepository,
        projects: ProjectRepository,
        filters: FilterRepository,
    ) -> None:
        self._tasks = tasks
        self._users = users
        self._projects = projects
        self._filters = filters
        self._current_user: User | None = None

        self._handlers: dict[MenuChoice, Callable[[], None]] = {
            MenuChoice.SEARCH: self.search_menu,
            MenuChoice.FILTER: self.filter_menu,
            MenuChoice.SEARCH_AND_FILTER: self.search_and_filter_menu,
            MenuChoice.SAVE_FILTER: self.save_filter_menu,
            MenuChoice.SHOW_FILTERS: self.show_filters_menu,
            MenuChoice.DELETE_FILTER: self.delete_filter_menu,
            MenuChoice.SHOW_TASKS: self.show_tasks_menu,
            MenuChoice.CREATE_TASK: self.create_task_menu,
            MenuChoice.SHOW_PROJECTS: self.show_projects_menu,
            MenuChoice.CREATE_PROJECT: self.create_project_menu,
            MenuChoice.SHOW_USERS: self.show_users_menu,
            MenuChoice.CREATE_USER: self.create_user_menu,
        }

    @property
    def current_user(self) -> User:
        """Возвращает вошедшего пользователя."""

        if self._current_user is None:
            raise RuntimeError("Пользователь не вошёл в систему.")

        return self._current_user

    def run(self) -> None:
        """Выполняет вход и запускает главный цикл меню."""

        if not self._login():
            print("Программа завершена.")
            return

        while True:
            self._print_menu()
            choice = self._read_choice(MenuChoice, "Выберите действие: ")

            if choice is None:
                print("Такого пункта меню нет.")
                logger.warning("Выбран несуществующий пункт меню")
                continue

            if choice is MenuChoice.EXIT:
                logger.info("Пользователь '%s' вышел", self.current_user.username)
                print("Программа завершена.")
                return

            logger.info(
                "Пользователь '%s' выбрал действие %s",
                self.current_user.username,
                choice.name,
            )

            try:
                self._handlers[choice]()
            except CLIError as error:
                print(error)
                logger.warning("Действие %s отклонено: %s", choice.name, error)

    # --- вход и меню ---

    def _login(self) -> bool:
        """Запрашивает логин; возвращает False, если пользователь отказался."""

        print("\n=== TASKICH: вход ===")
        for user in self._users.list_all():
            print(f"- {user.username} ({user.role})")

        while True:
            username = input("Введите логин или оставьте пустым для выхода: ").strip()

            if not username:
                return False

            user = self._users.get_by_username(username)

            if user is None:
                print("Пользователь не найден.")
                logger.warning("Неудачная попытка входа: '%s'", username)
                continue

            self._current_user = user
            print(f"Здравствуйте, {user.full_name}! Роль: {user.role}.")
            logger.info("Вход выполнен: '%s' (%s)", user.username, user.role)
            return True

    @staticmethod
    def _print_menu() -> None:
        """Печатает главное меню; номера берутся из MenuChoice."""

        print("\n=== TASKICH ===")

        for choice in MenuChoice:
            if choice is not MenuChoice.EXIT:
                print(f"{choice.value}. {MENU_TITLES[choice]}")

        print(f"{MenuChoice.EXIT.value}. {MENU_TITLES[MenuChoice.EXIT]}")

    # --- поиск и фильтры ---

    def search_menu(self) -> None:
        """Запрашивает поисковый запрос и выводит найденные задачи."""

        query = input("Введите поисковый запрос: ").strip()
        self._print_tasks(search_tasks(self._tasks.list_all(), query))

    def filter_menu(self) -> None:
        """Запрашивает параметры фильтрации и выводит подходящие задачи."""

        params = self._read_filter_params(with_query=False)
        self._print_tasks(filter_tasks(self._tasks.list_all(), **params))

    def search_and_filter_menu(self) -> None:
        """Выполняет поиск и фильтрацию задач по введённым параметрам."""

        params = self._read_filter_params(with_query=True)
        self._print_tasks(search_and_filter_tasks(self._tasks.list_all(), **params))

    def save_filter_menu(self) -> None:
        """Создаёт и сохраняет фильтр на основе введённых параметров."""

        name = input("Введите название фильтра: ").strip()

        if not name:
            raise CLIError("Название фильтра не может быть пустым.")

        params = self._read_filter_params(with_query=True)
        self._filters.save(SavedFilter(name=name, **params))
        print(f"Фильтр '{name}' сохранён.")

    def show_filters_menu(self) -> None:
        """Показывает сохранённые фильтры и позволяет применить выбранный."""

        saved_filters = self._filters.list_all()

        if not saved_filters:
            print("Сохранённых фильтров нет.")
            return

        print("\nСохранённые фильтры:")

        for saved_filter in saved_filters:
            print(f"- {saved_filter.name}")

        name = input(
            "Введите название фильтра для применения или оставьте пустым для выхода: "
        ).strip()

        if not name:
            return

        saved_filter = self._filters.get(name)

        if saved_filter is None:
            raise CLIError("Фильтр с таким названием не найден.")

        self._print_tasks(apply_saved_filter(self._tasks.list_all(), saved_filter))

    def delete_filter_menu(self) -> None:
        """Удаляет сохранённый фильтр по его названию."""

        name = input("Введите название фильтра для удаления: ").strip()

        if not name:
            raise CLIError("Название фильтра не может быть пустым.")

        if not self._filters.delete(name):
            raise CLIError("Фильтр с таким названием не найден.")

        print(f"Фильтр '{name}' удалён.")

    # --- задачи, проекты, пользователи ---

    def show_tasks_menu(self) -> None:
        """Выводит все задачи."""

        self._print_tasks(self._tasks.list_all())

    def create_task_menu(self) -> None:
        """Создаёт задачу; исполнитель и проект необязательны."""

        title = input("Введите название задачи: ").strip()

        if not title:
            raise CLIError("Название задачи не может быть пустым.")

        description = input("Введите описание: ").strip()
        tags = self._read_tags()
        status = self._read_optional_value(
            f"Введите статус (по умолчанию {DEFAULT_STATUS}): "
        )
        priority = self._read_optional_value(
            f"Введите приоритет (по умолчанию {DEFAULT_PRIORITY}): "
        )
        assignee_id = self._read_assignee_id()
        project_id = self._read_project_id()

        task = Task(
            id=self._tasks.next_id(),
            title=title,
            description=description,
            tags=tags,
            status=status or DEFAULT_STATUS,
            priority=priority or DEFAULT_PRIORITY,
            assignee_id=assignee_id,
            project_id=project_id,
        )
        self._tasks.add(task)
        print(f"Задача [{task.id}] создана.")

    def show_projects_menu(self) -> None:
        """Выводит проекты с руководителем и числом задач."""

        projects = self._projects.list_all()

        if not projects:
            print("Проектов нет.")
            return

        for project in projects:
            manager = self._user_name(project.manager_id) or "не назначен"
            tasks_count = len(self._tasks.list_by_project(project.id))

            print(
                f"\n[{project.id}] {project.name}\n"
                f"Описание: {project.description or 'нет'}\n"
                f"Руководитель: {manager}\n"
                f"Задач: {tasks_count}"
            )

    def create_project_menu(self) -> None:
        """Создаёт проект; доступно ролям Admin и Project Manager."""

        if not self.current_user.can_manage_projects:
            raise CLIError("Недостаточно прав: проекты создают Admin и Project Manager.")

        name = input("Введите название проекта: ").strip()

        if not name:
            raise CLIError("Название проекта не может быть пустым.")

        description = input("Введите описание: ").strip()
        manager_id = self._read_assignee_id(
            "Введите логин руководителя или оставьте пустым (это вы): "
        )

        if manager_id is None:
            manager_id = self.current_user.id

        manager = self._users.get(manager_id)

        if manager is None or not manager.can_manage_projects:
            raise CLIError("Руководителем может быть Admin или Project Manager.")

        project = Project(
            id=self._projects.next_id(),
            name=name,
            description=description,
            manager_id=manager_id,
        )
        self._projects.add(project)
        print(f"Проект [{project.id}] '{project.name}' создан.")

    def show_users_menu(self) -> None:
        """Выводит список пользователей."""

        for user in self._users.list_all():
            print(f"[{user.id}] {user.username} — {user.full_name} ({user.role})")

    def create_user_menu(self) -> None:
        """Создаёт пользователя; доступно только роли Admin."""

        if not self.current_user.is_admin:
            raise CLIError("Недостаточно прав: пользователей создаёт только Admin.")

        username = input("Введите логин: ").strip()

        if not username:
            raise CLIError("Логин не может быть пустым.")

        if self._users.get_by_username(username) is not None:
            raise CLIError(f"Логин '{username}' уже занят.")

        full_name = input("Введите полное имя: ").strip() or username

        print("Роли:")
        for role_choice in RoleChoice:
            print(f"{role_choice.value}. {ROLE_BY_CHOICE[role_choice]}")

        role_choice = self._read_choice(RoleChoice, "Выберите роль: ")

        if role_choice is None:
            raise CLIError("Такой роли нет.")

        user = User(
            id=self._users.next_id(),
            username=username,
            full_name=full_name,
            role=ROLE_BY_CHOICE[role_choice],
        )
        self._users.add(user)
        print(f"Пользователь '{user.username}' ({user.role}) создан.")

    # --- чтение ввода ---

    @staticmethod
    def _read_choice(choice_enum: type[ChoiceT], prompt: str) -> ChoiceT | None:
        """Читает число и возвращает элемент IntEnum или None, если ввод неверный."""

        value = input(prompt).strip()

        try:
            return choice_enum(int(value))
        except ValueError:
            return None

    @staticmethod
    def _read_optional_value(prompt: str) -> str | None:
        """Возвращает введённое значение или None для пустого ввода."""

        value = input(prompt).strip()

        return value or None

    @staticmethod
    def _read_tags() -> list[str]:
        """Запрашивает список тегов через запятую и возвращает его."""

        value = input("Введите теги через запятую или оставьте пустым: ").strip()

        return [tag.strip() for tag in value.split(",") if tag.strip()]

    def _read_assignee_id(
        self,
        prompt: str = "Введите логин исполнителя или оставьте пустым: ",
    ) -> int | None:
        """Читает логин и возвращает id пользователя; ошибка, если логина нет."""

        username = self._read_optional_value(prompt)

        if username is None:
            return None

        user = self._users.get_by_username(username)

        if user is None:
            raise CLIError(f"Пользователь '{username}' не найден.")

        return user.id

    def _read_project_id(self) -> int | None:
        """Читает id проекта; ошибка, если ввод не число или проекта нет."""

        value = self._read_optional_value("Введите ID проекта или оставьте пустым: ")

        if value is None:
            return None

        if not value.isdigit():
            raise CLIError("ID проекта должен быть числом.")

        project = self._projects.get(int(value))

        if project is None:
            raise CLIError(f"Проект с id={value} не найден.")

        return project.id

    def _read_filter_params(self, *, with_query: bool) -> dict[str, Any]:
        """Читает параметры поиска и фильтрации в виде именованных аргументов."""

        params: dict[str, Any] = {}

        if with_query:
            params["query"] = self._read_optional_value(
                "Введите поисковый запрос или оставьте пустым: "
            )

        params["tags"] = self._read_tags()
        params["status"] = self._read_optional_value(
            "Введите статус или оставьте пустым: "
        )
        params["priority"] = self._read_optional_value(
            "Введите приоритет или оставьте пустым: "
        )
        params["assignee_id"] = self._read_assignee_id()
        params["project_id"] = self._read_project_id()

        return params

    # --- вывод ---

    def _user_name(self, user_id: int | None) -> str | None:
        """Возвращает полное имя пользователя или None."""

        user = self._users.get(user_id) if user_id is not None else None

        return user.full_name if user else None

    def _project_name(self, project_id: int | None) -> str | None:
        """Возвращает название проекта или None."""

        project = self._projects.get(project_id) if project_id is not None else None

        return project.name if project else None

    def _print_tasks(self, tasks: list[Task]) -> None:
        """Выводит найденные задачи в удобном для пользователя формате."""

        if not tasks:
            print("Задачи не найдены.")
            return

        print(f"\nНайдено задач: {len(tasks)}")

        for task in tasks:
            assignee = self._user_name(task.assignee_id) or "не назначен"
            project = self._project_name(task.project_id) or "без проекта"
            tags = ", ".join(task.tags) or "нет"

            print(
                f"\n[{task.id}] {task.title}\n"
                f"Описание: {task.description}\n"
                f"Проект: {project}\n"
                f"Теги: {tags}\n"
                f"Статус: {task.status}\n"
                f"Приоритет: {task.priority}\n"
                f"Исполнитель: {assignee}"
            )
