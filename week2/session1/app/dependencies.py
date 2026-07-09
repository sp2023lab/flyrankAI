from functools import lru_cache

from app.repositories.interface import ItemRepository
from app.repositories.postgres_repository import PostgresItemRepository
from app.service import ItemService


@lru_cache
def get_repository() -> ItemRepository:
    return PostgresItemRepository()


def get_item_service() -> ItemService:
    return ItemService(get_repository())