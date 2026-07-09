from typing import Protocol

from app.models import Item, ItemCreate, ItemUpdate


class ItemRepository(Protocol):
    def create(self, item: ItemCreate) -> Item:
        ...

    def list_all(self) -> list[Item]:
        ...

    def get_by_id(self, item_id: int) -> Item | None:
        ...

    def update(self, item_id: int, item: ItemUpdate) -> Item | None:
        ...

    def delete(self, item_id: int) -> bool:
        ...