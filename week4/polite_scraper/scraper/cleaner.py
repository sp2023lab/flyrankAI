"""Cleaning and normalisation helpers."""

from __future__ import annotations

import re
from urllib.parse import urljoin


_RATING_MAP = {
    "Zero": 0,
    "One": 1,
    "Two": 2,
    "Three": 3,
    "Four": 4,
    "Five": 5,
}


def clean_text(value: str | None) -> str:
    """Collapse repeated whitespace and safely handle missing text."""

    return " ".join((value or "").split())


def clean_price(value: str | None) -> float:
    """Convert a displayed GBP price such as '£51.77' into a float."""

    text = clean_text(value)
    match = re.search(r"-?\d+(?:\.\d+)?", text.replace(",", ""))
    if not match:
        raise ValueError(f"Could not parse price from {value!r}")
    return float(match.group(0))


def clean_availability(value: str | None) -> str:
    """Normalise availability text to a stable machine-readable value."""

    text = clean_text(value).lower()
    if "in stock" in text:
        return "in_stock"
    if "out of stock" in text:
        return "out_of_stock"
    return "unknown"


def clean_rating(classes: list[str] | tuple[str, ...] | None) -> int:
    """Convert a CSS class such as 'Three' into the integer 3."""

    for class_name in classes or []:
        if class_name in _RATING_MAP:
            return _RATING_MAP[class_name]
    return 0


def absolute_url(base_url: str, href: str | None) -> str:
    """Resolve a relative URL against the page on which it appeared."""

    if not href:
        raise ValueError("A URL was expected but no href/src value was present")
    return urljoin(base_url, href)
