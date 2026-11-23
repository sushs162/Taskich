from abc import ABC, abstractmethod
import logging
from sqlalchemy import select
from sqlalchemy.orm import Session
from taskich.database.orm_models import UserRecord
from taskich.models import User, UserRole
logger = logging.getLogger(__name__)

class UserRepository(ABC):
    """Абстрактный контракт репозитория для соответствующей сущности."""

    @abstractmethod
    def next_id(self) -> int:
        raise NotImplementedError

    @abstractmethod
    def add(self, user: User) -> None:
        raise NotImplementedError

    @abstractmethod
    def get(self, user_id: int) -> User | None:
        raise NotImplementedError

    @abstractmethod
    def get_by_username(self, username: str) -> User | None:
        raise NotImplementedError

    @abstractmethod
    def delete(self, user_id: int) -> bool:
        raise NotImplementedError

    @abstractmethod
    def list_all(self) -> list[User]:
        raise NotImplementedError

class InMemoryUserRepository(UserRepository):
    """Хранит пользователей в памяти во время работы программы."""

    def __init__(self) -> None:
        self._users: dict[int, User] = {}

    def next_id(self) -> int:
        """Возвращает максимальный идентификатор плюс один."""
        return max(self._users, default=0) + 1

    def add(self, user: User) -> None:
        """Добавляет пользователя; id и логин должны быть уникальными."""
        if user.id in self._users:
            raise ValueError(f'Пользователь с id={user.id} уже существует.')
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
            logger.warning('Попытка удалить несуществующего пользователя id=%s', user_id)
            return False
        del self._users[user_id]
        logger.info('Удалён пользователь id=%s', user_id)
        return True

    def list_all(self) -> list[User]:
        """Возвращает список всех пользователей."""
        return list(self._users.values())

class SqlAlchemyUserRepository(UserRepository):

    def __init__(self, session: Session):
        self.session = session

    @staticmethod
    def _domain(r: UserRecord) -> User:
        return User(r.id, r.username, r.full_name, UserRole(r.role))

    def next_id(self) -> int:
        return (self.session.scalar(select(UserRecord.id).order_by(UserRecord.id.desc()).limit(1)) or 0) + 1

    def add(self, user: User) -> None:
        self.session.add(UserRecord(id=user.id, username=user.username, full_name=user.full_name, role=user.role.value))

    def get(self, user_id: int) -> User | None:
        r = self.session.get(UserRecord, user_id)
        return self._domain(r) if r else None

    def get_by_username(self, username: str) -> User | None:
        r = self.session.scalar(select(UserRecord).where(UserRecord.username.ilike(username.strip())))
        return self._domain(r) if r else None

    def delete(self, user_id: int) -> bool:
        r = self.session.get(UserRecord, user_id)
        if not r:
            return False
        self.session.delete(r)
        return True

    def list_all(self) -> list[User]:
        return [self._domain(r) for r in self.session.scalars(select(UserRecord).order_by(UserRecord.id))]
