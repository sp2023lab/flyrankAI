from datetime import datetime, UTC

from app.models import Item, ItemCreate, ItemUpdate


class InMemoryItemRepository:
    def __init__(self) -> None:
        self.items: dict[int, Item] = {}
        self.next_id = 1

    def create(self, item: ItemCreate) -> Item:
        new_item = Item(
            id=self.next_id,
            name=item.name,
            description=item.description,
            created_at=datetime.now(UTC),
        )
        self.items[self.next_id] = new_item
        self.next_id += 1
        return new_item

    def list_all(self) -> list[Item]:
        return list(self.items.values())

    def get_by_id(self, item_id: int) -> Item | None:
        return self.items.get(item_id)

    def update(self, item_id: int, item: ItemUpdate) -> Item | None:
        existing = self.items.get(item_id)

        if existing is None:
            return None

        updated = existing.model_copy(
            update={
                "name": item.name if item.name is not None else existing.name,
                "description": (
                    item.description
                    if item.description is not None
                    else existing.description
                ),
            }
        )

        self.items[item_id] = updated
        return updated

    def delete(self, item_id: int) -> bool:
        if item_id not in self.items:
            return False

        del self.items[item_id]
        return True