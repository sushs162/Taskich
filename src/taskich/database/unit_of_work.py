"""Unit of Work: одна SQLAlchemy Session на бизнес-операцию."""

from taskich.database.connection import SessionFactory
from taskich.repositories.filter import SqlAlchemyFilterRepository
from taskich.repositories.project import SqlAlchemyProjectRepository
from taskich.repositories.task import SqlAlchemyTaskRepository
from taskich.repositories.user import SqlAlchemyUserRepository


class SqlAlchemyUnitOfWork:
    """Объединяет репозитории в одну транзакционную единицу работы."""

    def __enter__(self):
        self.session = SessionFactory()
        self.tasks = SqlAlchemyTaskRepository(self.session)
        self.users = SqlAlchemyUserRepository(self.session)
        self.projects = SqlAlchemyProjectRepository(self.session)
        self.filters = SqlAlchemyFilterRepository(self.session)
        return self

    def __exit__(self, exc_type, exc, tb):
        if exc_type:
            self.rollback()
        self.session.close()

    def commit(self) -> None:
        self.session.commit()

    def rollback(self) -> None:
        self.session.rollback()
