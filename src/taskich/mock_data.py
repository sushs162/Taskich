from taskich.models import Project, Task, User, UserRole


def create_demo_users() -> list[User]:
    """Создаёт демонстрационных пользователей со всеми ролями."""

    return [
        User(id=1, username="alice", full_name="Алиса Админова", role=UserRole.ADMIN),
        User(
            id=2,
            username="bob",
            full_name="Борис Менеджеров",
            role=UserRole.PROJECT_MANAGER,
        ),
        User(id=3, username="charlie", full_name="Чарли Пользователев"),
    ]


def create_demo_projects() -> list[Project]:
    """Создаёт демонстрационные проекты."""

    return [
        Project(
            id=1,
            name="Серверная часть",
            description="Авторизация, база данных и тесты.",
            manager_id=2,
        ),
        Project(
            id=2,
            name="Клиентская часть и документация",
            description="Интерфейс поиска и документация проекта.",
            manager_id=2,
        ),
    ]


def create_demo_tasks() -> list[Task]:
    """Создаёт набор демонстрационных задач для работы приложения."""

    return [
        Task(
            id=1,
            title="Настроить авторизацию",
            description="Добавить регистрацию и вход пользователей.",
            tags=["backend", "auth"],
            status="todo",
            priority="high",
            assignee_id=1,
            project_id=1,
        ),
        Task(
            id=2,
            title="Создать интерфейс поиска",
            description="Реализовать поиск задач по названию и описанию.",
            tags=["frontend", "search"],
            status="in-progress",
            priority="medium",
            assignee_id=2,
            project_id=2,
        ),
        Task(
            id=3,
            title="Написать документацию",
            description="Подготовить документацию для пользователей проекта.",
            tags=["docs"],
            status="done",
            priority="low",
            assignee_id=1,
            project_id=2,
        ),
        Task(
            id=4,
            title="Настроить базу данных",
            description="Подключить SQLAlchemy и подготовить модели.",
            tags=["backend", "database"],
            status="todo",
            priority="high",
            assignee_id=3,
            project_id=1,
        ),
        Task(
            id=5,
            title="Добавить автоматические тесты",
            description="Покрыть основные функции приложения тестами.",
            tags=["testing", "backend"],
            status="todo",
            priority="medium",
            assignee_id=2,
            project_id=1,
        ),
    ]
