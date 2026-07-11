"""Structured records produced by the scraper."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class BookRecord:
    """A cleaned record extracted from a book listing."""

    title: str
    price_gbp: float
    availability: str
    rating: int
    product_url: str
    image_url: str
    source_url: str

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serialisable dictionary."""

        return asdict(self)
