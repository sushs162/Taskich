"""Настройка SQLAlchemy и SQLite."""
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker


class Base(DeclarativeBase):
    pass


DB_PATH = Path("taskich.db")
DATABASE_URL = f"sqlite:///{DB_PATH.resolve()}"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionFactory = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


def init_database() -> None:
    # Импорт регистрирует ORM-модели в metadata.
    from taskich.database import orm_models  # noqa: F401
    Base.metadata.create_all(bind=engine)
