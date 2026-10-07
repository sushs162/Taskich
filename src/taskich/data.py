from taskich.models import Task


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
            assignee="alice",
        ),
        Task(
            id=2,
            title="Создать интерфейс поиска",
            description="Реализовать поиск задач по названию и описанию.",
            tags=["frontend", "search"],
            status="in-progress",
            priority="medium",
            assignee="bob",
        ),
        Task(
            id=3,
            title="Написать документацию",
            description="Подготовить документацию для пользователей проекта.",
            tags=["docs"],
            status="done",
            priority="low",
            assignee="alice",
        ),
        Task(
            id=4,
            title="Настроить базу данных",
            description="Подключить SQLAlchemy и подготовить модели.",
            tags=["backend", "database"],
            status="todo",
            priority="high",
            assignee="charlie",
        ),
        Task(
            id=5,
            title="Добавить автоматические тесты",
            description="Покрыть основные функции приложения тестами.",
            tags=["testing", "backend"],
            status="todo",
            priority="medium",
            assignee="bob",
        ),
    ]
