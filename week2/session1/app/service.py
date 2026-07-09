from app.models import Item, ItemCreate, ItemUpdate
from app.repositories.interface import ItemRepository


class ItemService:
    def __init__(self, repository: ItemRepository) -> None:
        self.repository = repository

    def create_item(self, item: ItemCreate) -> Item:
        return self.repository.create(item)

    def list_items(self) -> list[Item]:
        return self.repository.list_all()

    def get_item(self, item_id: int) -> Item | None:
        return self.repository.get_by_id(item_id)

    def update_item(self, item_id: int, item: ItemUpdate) -> Item | None:
        return self.repository.update(item_id, item)

    def delete_item(self, item_id: int) -> bool:
        return self.repository.delete(item_id)