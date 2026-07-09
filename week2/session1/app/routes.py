from fastapi import APIRouter, Depends, HTTPException, status

from app.dependencies import get_item_service
from app.models import Item, ItemCreate, ItemUpdate
from app.service import ItemService


router = APIRouter()


@router.get("/")
def root() -> dict[str, str]:
    return {"message": "FlyRank BE-04 API is running"}


@router.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


@router.post(
    "/items",
    response_model=Item,
    status_code=status.HTTP_201_CREATED,
)
def create_item(
    item: ItemCreate,
    service: ItemService = Depends(get_item_service),
) -> Item:
    return service.create_item(item)


@router.get("/items", response_model=list[Item])
def list_items(
    service: ItemService = Depends(get_item_service),
) -> list[Item]:
    return service.list_items()


@router.get("/items/{item_id}", response_model=Item)
def get_item(
    item_id: int,
    service: ItemService = Depends(get_item_service),
) -> Item:
    item = service.get_item(item_id)

    if item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found",
        )

    return item


@router.patch("/items/{item_id}", response_model=Item)
def update_item(
    item_id: int,
    item_update: ItemUpdate,
    service: ItemService = Depends(get_item_service),
) -> Item:
    item = service.update_item(item_id, item_update)

    if item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found",
        )

    return item


@router.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item(
    item_id: int,
    service: ItemService = Depends(get_item_service),
) -> None:
    deleted = service.delete_item(item_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found",
        )