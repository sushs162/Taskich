from abc import ABC, abstractmethod
import logging
from sqlalchemy import select
from sqlalchemy.orm import Session
from taskich.database.orm_models import ProjectRecord
from taskich.models import Project
logger = logging.getLogger(__name__)

class ProjectRepository(ABC):
    """Абстрактный контракт репозитория для соответствующей сущности."""

    @abstractmethod
    def next_id(self) -> int:
        raise NotImplementedError

    @abstractmethod
    def add(self, project: Project) -> None:
        raise NotImplementedError

    @abstractmethod
    def get(self, project_id: int) -> Project | None:
        raise NotImplementedError

    @abstractmethod
    def delete(self, project_id: int) -> bool:
        raise NotImplementedError

    @abstractmethod
    def list_all(self) -> list[Project]:
        raise NotImplementedError

class InMemoryProjectRepository(ProjectRepository):
    """Хранит проекты в памяти во время работы программы."""

    def __init__(self) -> None:
        self._projects: dict[int, Project] = {}

    def next_id(self) -> int:
        """Возвращает максимальный идентификатор плюс один."""
        return max(self._projects, default=0) + 1

    def add(self, project: Project) -> None:
        """Добавляет проект; повторный идентификатор считается ошибкой."""
        if project.id in self._projects:
            raise ValueError(f'Проект с id={project.id} уже существует.')
        self._projects[project.id] = project
        logger.info("Добавлен проект id=%s '%s'", project.id, project.name)

    def get(self, project_id: int) -> Project | None:
        """Возвращает проект по идентификатору."""
        return self._projects.get(project_id)

    def delete(self, project_id: int) -> bool:
        """Удаляет проект и сообщает об успешном удалении."""
        if project_id not in self._projects:
            logger.warning('Попытка удалить несуществующий проект id=%s', project_id)
            return False
        del self._projects[project_id]
        logger.info('Удалён проект id=%s', project_id)
        return True

    def list_all(self) -> list[Project]:
        """Возвращает список всех проектов."""
        return list(self._projects.values())

class SqlAlchemyProjectRepository(ProjectRepository):

    def __init__(self, session: Session):
        self.session = session

    @staticmethod
    def _domain(r: ProjectRecord) -> Project:
        return Project(r.id, r.name, r.description or '', r.manager_id)

    def next_id(self) -> int:
        return (self.session.scalar(select(ProjectRecord.id).order_by(ProjectRecord.id.desc()).limit(1)) or 0) + 1

    def add(self, project: Project) -> None:
        self.session.add(ProjectRecord(id=project.id, name=project.name, description=project.description, manager_id=project.manager_id))

    def get(self, project_id: int) -> Project | None:
        r = self.session.get(ProjectRecord, project_id)
        return self._domain(r) if r else None

    def delete(self, project_id: int) -> bool:
        r = self.session.get(ProjectRecord, project_id)
        if not r:
            return False
        self.session.delete(r)
        return True

    def list_all(self) -> list[Project]:
        return [self._domain(r) for r in self.session.scalars(select(ProjectRecord).order_by(ProjectRecord.id))]
