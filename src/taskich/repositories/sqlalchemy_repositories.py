"""SQLAlchemy-реализации Repository."""
from sqlalchemy import select
from sqlalchemy.orm import Session
from taskich.database.orm_models import UserRecord, ProjectRecord, TaskRecord, SavedFilterRecord
from taskich.models import User, UserRole, Project, Task, SavedFilter


class SqlAlchemyTaskRepository:
    def __init__(self, session: Session): self.session = session
    @staticmethod
    def _domain(r: TaskRecord) -> Task:
        return Task(r.id, r.title, r.description, list(r.tags or []), r.status, r.priority, r.assignee_id, r.project_id)
    def next_id(self) -> int:
        return (self.session.scalar(select(TaskRecord.id).order_by(TaskRecord.id.desc()).limit(1)) or 0) + 1
    def add(self, task: Task) -> None:
        self.session.add(TaskRecord(id=task.id, title=task.title, description=task.description, tags=task.tags, status=task.status, priority=task.priority, assignee_id=task.assignee_id, project_id=task.project_id))
    def get(self, task_id: int) -> Task | None:
        r = self.session.get(TaskRecord, task_id); return self._domain(r) if r else None
    def update(self, task: Task) -> bool:
        r = self.session.get(TaskRecord, task.id)
        if not r: return False
        r.title, r.description, r.tags, r.status, r.priority, r.assignee_id, r.project_id = task.title, task.description, task.tags, task.status, task.priority, task.assignee_id, task.project_id
        return True
    def delete(self, task_id: int) -> bool:
        r = self.session.get(TaskRecord, task_id)
        if not r: return False
        self.session.delete(r); return True
    def list_all(self) -> list[Task]: return [self._domain(r) for r in self.session.scalars(select(TaskRecord).order_by(TaskRecord.id))]
    def list_by_project(self, project_id: int) -> list[Task]: return [t for t in self.list_all() if t.project_id == project_id]
    def list_by_assignee(self, user_id: int) -> list[Task]: return [t for t in self.list_all() if t.assignee_id == user_id]


class SqlAlchemyUserRepository:
    def __init__(self, session: Session): self.session = session
    @staticmethod
    def _domain(r: UserRecord) -> User: return User(r.id, r.username, r.full_name, UserRole(r.role))
    def next_id(self) -> int: return (self.session.scalar(select(UserRecord.id).order_by(UserRecord.id.desc()).limit(1)) or 0) + 1
    def add(self, user: User) -> None: self.session.add(UserRecord(id=user.id, username=user.username, full_name=user.full_name, role=user.role.value))
    def get(self, user_id: int) -> User | None:
        r = self.session.get(UserRecord, user_id); return self._domain(r) if r else None
    def get_by_username(self, username: str) -> User | None:
        r = self.session.scalar(select(UserRecord).where(UserRecord.username.ilike(username.strip())))
        return self._domain(r) if r else None
    def delete(self, user_id: int) -> bool:
        r = self.session.get(UserRecord, user_id)
        if not r: return False
        self.session.delete(r); return True
    def list_all(self) -> list[User]: return [self._domain(r) for r in self.session.scalars(select(UserRecord).order_by(UserRecord.id))]


class SqlAlchemyProjectRepository:
    def __init__(self, session: Session): self.session = session
    @staticmethod
    def _domain(r: ProjectRecord) -> Project: return Project(r.id, r.name, r.description or "", r.manager_id)
    def next_id(self) -> int: return (self.session.scalar(select(ProjectRecord.id).order_by(ProjectRecord.id.desc()).limit(1)) or 0) + 1
    def add(self, project: Project) -> None: self.session.add(ProjectRecord(id=project.id, name=project.name, description=project.description, manager_id=project.manager_id))
    def get(self, project_id: int) -> Project | None:
        r = self.session.get(ProjectRecord, project_id); return self._domain(r) if r else None
    def delete(self, project_id: int) -> bool:
        r = self.session.get(ProjectRecord, project_id)
        if not r: return False
        self.session.delete(r); return True
    def list_all(self) -> list[Project]: return [self._domain(r) for r in self.session.scalars(select(ProjectRecord).order_by(ProjectRecord.id))]


class SqlAlchemyFilterRepository:
    def __init__(self, session: Session): self.session = session
    @staticmethod
    def _domain(r: SavedFilterRecord) -> SavedFilter: return SavedFilter(r.name, r.query, list(r.tags or []), r.status, r.priority, r.assignee_id, r.project_id)
    def save(self, f: SavedFilter) -> None:
        r = self.session.get(SavedFilterRecord, f.name)
        if r is None: r = SavedFilterRecord(name=f.name); self.session.add(r)
        r.query, r.tags, r.status, r.priority, r.assignee_id, r.project_id = f.query, f.tags, f.status, f.priority, f.assignee_id, f.project_id
    def get(self, name: str) -> SavedFilter | None:
        r = self.session.get(SavedFilterRecord, name); return self._domain(r) if r else None
    def delete(self, name: str) -> bool:
        r = self.session.get(SavedFilterRecord, name)
        if not r: return False
        self.session.delete(r); return True
    def list_all(self) -> list[SavedFilter]: return [self._domain(r) for r in self.session.scalars(select(SavedFilterRecord).order_by(SavedFilterRecord.name))]
