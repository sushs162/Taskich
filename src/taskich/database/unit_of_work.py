"""Unit of Work: одна SQLAlchemy Session на бизнес-операцию."""
from taskich.database.connection import SessionFactory
from taskich.repositories.sqlalchemy_repositories import (SqlAlchemyTaskRepository, SqlAlchemyUserRepository, SqlAlchemyProjectRepository, SqlAlchemyFilterRepository)


class SqlAlchemyUnitOfWork:
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
    def commit(self): self.session.commit()
    def rollback(self): self.session.rollback()
