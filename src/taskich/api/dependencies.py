from taskich.services.task_service import TaskService
from taskich.services.catalog_service import CatalogService


def get_task_service() -> TaskService:
    return TaskService()


def get_catalog_service() -> CatalogService:
    return CatalogService()
