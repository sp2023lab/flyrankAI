import os

import psycopg
from psycopg.rows import dict_row

from app.models import Item, ItemCreate, ItemUpdate


class PostgresItemRepository:
    def __init__(self) -> None:
        self.database_url = os.environ["DATABASE_URL"]

    def _connect(self):
        return psycopg.connect(self.database_url, row_factory=dict_row)

    def create(self, item: ItemCreate) -> Item:
        with self._connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO items (name, description)
                    VALUES (%s, %s)
                    RETURNING id, name, description, created_at;
                    """,
                    (item.name, item.description),
                )
                row = cur.fetchone()
                return Item(**row)

    def list_all(self) -> list[Item]:
        with self._connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT id, name, description, created_at
                    FROM items
                    ORDER BY id;
                    """
                )
                rows = cur.fetchall()
                return [Item(**row) for row in rows]

    def get_by_id(self, item_id: int) -> Item | None:
        with self._connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT id, name, description, created_at
                    FROM items
                    WHERE id = %s;
                    """,
                    (item_id,),
                )
                row = cur.fetchone()
                return Item(**row) if row else None

    def update(self, item_id: int, item: ItemUpdate) -> Item | None:
        existing = self.get_by_id(item_id)

        if existing is None:
            return None

        new_name = item.name if item.name is not None else existing.name
        new_description = (
            item.description if item.description is not None else existing.description
        )

        with self._connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    UPDATE items
                    SET name = %s,
                        description = %s
                    WHERE id = %s
                    RETURNING id, name, description, created_at;
                    """,
                    (new_name, new_description, item_id),
                )
                row = cur.fetchone()
                return Item(**row) if row else None

    def delete(self, item_id: int) -> bool:
        with self._connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    DELETE FROM items
                    WHERE id = %s;
                    """,
                    (item_id,),
                )
                return cur.rowcount > 0