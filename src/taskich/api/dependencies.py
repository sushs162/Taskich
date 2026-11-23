from taskich.services.catalog import CatalogService
from taskich.services.task import TaskService


def get_task_service() -> TaskService:
    return TaskService()


def get_catalog_service() -> CatalogService:
    return CatalogService()
