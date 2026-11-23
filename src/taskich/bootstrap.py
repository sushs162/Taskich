"""Инициализация БД и минимальные демонстрационные данные при первом запуске."""
from taskich.database.connection import init_database
from taskich.database.unit_of_work import SqlAlchemyUnitOfWork
from taskich.mock_data import create_demo_users, create_demo_projects, create_demo_tasks


def initialize_application() -> None:
    init_database()
    with SqlAlchemyUnitOfWork() as uow:
        if uow.users.list_all():
            return
        for user in create_demo_users(): uow.users.add(user)
        for project in create_demo_projects(): uow.projects.add(project)
        for task in create_demo_tasks(): uow.tasks.add(task)
        uow.commit()
