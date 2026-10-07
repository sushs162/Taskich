from taskich.models import SavedFilter, Task
from taskich.search import (
    apply_saved_filter,
    filter_tasks,
    search_and_filter_tasks,
    search_tasks,
)
from taskich.storage import FilterRepository


def run_cli(
    tasks: list[Task],
    filter_repository: FilterRepository,
) -> None:
    """Запускает интерактивное меню Taskich в терминале."""

    while True:
        print("\n=== TASKICH ===")
        print("1. Поиск задач")
        print("2. Фильтрация задач")
        print("3. Поиск + фильтрация")
        print("4. Сохранить фильтр")
        print("5. Сохранённые фильтры")
        print("6. Удалить фильтр")
        print("0. Выход")

        choice = input("Выберите действие: ").strip()

        if choice == "1":
            search_menu(tasks)
        elif choice == "2":
            filter_menu(tasks)
        elif choice == "3":
            search_and_filter_menu(tasks)
        elif choice == "4":
            save_filter_menu(filter_repository)
        elif choice == "5":
            show_filters_menu(tasks, filter_repository)
        elif choice == "6":
            delete_filter_menu(filter_repository)
        elif choice == "0":
            print("Программа завершена.")
            return
        else:
            print("Такого пункта меню нет.")


def search_menu(tasks: list[Task]) -> None:
    """Запрашивает поисковый запрос и выводит найденные задачи."""

    query = input("Введите поисковый запрос: ").strip()
    result = search_tasks(tasks, query)
    print_tasks(result)


def filter_menu(tasks: list[Task]) -> None:
    """Запрашивает параметры фильтрации и выводит подходящие задачи."""

    tags = read_tags()
    status = read_optional_value("Введите статус или оставьте пустым: ")
    priority = read_optional_value("Введите приоритет или оставьте пустым: ")
    assignee = read_optional_value("Введите исполнителя или оставьте пустым: ")

    result = filter_tasks(
        tasks,
        tags=tags,
        status=status,
        priority=priority,
        assignee=assignee,
    )
    print_tasks(result)


def search_and_filter_menu(tasks: list[Task]) -> None:
    """Выполняет поиск и фильтрацию задач по введённым параметрам."""

    query = read_optional_value("Введите поисковый запрос или оставьте пустым: ")
    tags = read_tags()
    status = read_optional_value("Введите статус или оставьте пустым: ")
    priority = read_optional_value("Введите приоритет или оставьте пустым: ")
    assignee = read_optional_value("Введите исполнителя или оставьте пустым: ")

    result = search_and_filter_tasks(
        tasks,
        query=query,
        tags=tags,
        status=status,
        priority=priority,
        assignee=assignee,
    )
    print_tasks(result)


def save_filter_menu(
    filter_repository: FilterRepository,
) -> None:
    """Создаёт и сохраняет фильтр на основе введённых параметров."""

    name = input("Введите название фильтра: ").strip()

    if not name:
        print("Название фильтра не может быть пустым.")
        return

    query = read_optional_value("Введите поисковый запрос или оставьте пустым: ")
    tags = read_tags()
    status = read_optional_value("Введите статус или оставьте пустым: ")
    priority = read_optional_value("Введите приоритет или оставьте пустым: ")
    assignee = read_optional_value("Введите исполнителя или оставьте пустым: ")

    saved_filter = SavedFilter(
        name=name,
        query=query,
        tags=tags,
        status=status,
        priority=priority,
        assignee=assignee,
    )

    filter_repository.save(saved_filter)
    print(f"Фильтр '{name}' сохранён.")


def show_filters_menu(
    tasks: list[Task],
    filter_repository: FilterRepository,
) -> None:
    """Показывает сохранённые фильтры и позволяет применить выбранный."""

    saved_filters = filter_repository.list_all()

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

    saved_filter = filter_repository.get(name)

    if saved_filter is None:
        print("Фильтр с таким названием не найден.")
        return

    result = apply_saved_filter(tasks, saved_filter)
    print_tasks(result)


def delete_filter_menu(
    filter_repository: FilterRepository,
) -> None:
    """Удаляет сохранённый фильтр по его названию."""

    name = input("Введите название фильтра для удаления: ").strip()

    if not name:
        print("Название фильтра не может быть пустым.")
        return

    if filter_repository.delete(name):
        print(f"Фильтр '{name}' удалён.")
    else:
        print("Фильтр с таким названием не найден.")


def read_tags() -> list[str]:
    """Запрашивает список тегов через запятую и возвращает его."""

    value = input("Введите теги через запятую или оставьте пустым: ").strip()

    if not value:
        return []

    return [tag.strip() for tag in value.split(",") if tag.strip()]


def read_optional_value(prompt: str) -> str | None:
    """Возвращает введённое значение или None для пустого ввода."""

    value = input(prompt).strip()

    return value or None


def print_tasks(tasks: list[Task]) -> None:
    """Выводит найденные задачи в удобном для пользователя формате."""

    if not tasks:
        print("Задачи не найдены.")
        return

    print(f"\nНайдено задач: {len(tasks)}")

    for task in tasks:
        assignee = task.assignee or "не назначен"
        tags = ", ".join(task.tags) or "нет"

        print(
            f"\n[{task.id}] {task.title}\n"
            f"Описание: {task.description}\n"
            f"Теги: {tags}\n"
            f"Статус: {task.status}\n"
            f"Приоритет: {task.priority}\n"
            f"Исполнитель: {assignee}"
        )
