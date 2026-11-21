from taskich.database.unit_of_work import SqlAlchemyUnitOfWork
from taskich.models import Project, User, UserRole, SavedFilter


class CatalogService:
    """Service Layer для пользователей, проектов и сохранённых фильтров."""
    def __init__(self, uow_factory=SqlAlchemyUnitOfWork): self.uow_factory = uow_factory
    def list_users(self) -> list[User]:
        with self.uow_factory() as uow: return uow.users.list_all()
    def create_user(self, username: str, full_name: str, role: UserRole = UserRole.USER) -> User:
        with self.uow_factory() as uow:
            if uow.users.get_by_username(username): raise ValueError("Пользователь с таким логином уже существует")
            user = User(uow.users.next_id(), username, full_name, role); uow.users.add(user); uow.commit(); return user
    def list_projects(self) -> list[Project]:
        with self.uow_factory() as uow: return uow.projects.list_all()
    def create_project(self, name: str, description: str = "", manager_id: int | None = None) -> Project:
        with self.uow_factory() as uow:
            project = Project(uow.projects.next_id(), name, description, manager_id); uow.projects.add(project); uow.commit(); return project
    def get_filter(self, name: str) -> SavedFilter | None:
        with self.uow_factory() as uow: return uow.filters.get(name)
    def list_filters(self) -> list[SavedFilter]:
        with self.uow_factory() as uow: return uow.filters.list_all()
    def save_filter(self, saved_filter: SavedFilter) -> SavedFilter:
        with self.uow_factory() as uow: uow.filters.save(saved_filter); uow.commit(); return saved_filter
    def delete_filter(self, name: str) -> bool:
        with self.uow_factory() as uow:
            deleted = uow.filters.delete(name)
            if deleted: uow.commit()
            return deleted
