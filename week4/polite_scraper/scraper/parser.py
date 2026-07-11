"""HTML parsing for Books to Scrape listing pages."""

from __future__ import annotations

import logging
from dataclasses import dataclass

from bs4 import BeautifulSoup, Tag

from .cleaner import (
    absolute_url,
    clean_availability,
    clean_price,
    clean_rating,
    clean_text,
)
from .models import BookRecord

LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class ParsedPage:
    records: list[BookRecord]
    next_url: str | None


def _required_tag(parent: Tag, selector: str, field_name: str) -> Tag:
    tag = parent.select_one(selector)
    if not isinstance(tag, Tag):
        raise ValueError(f"Missing required field {field_name!r} using selector {selector!r}")
    return tag


def parse_listing_page(html: str, source_url: str) -> ParsedPage:
    """Extract cleaned book records and the next catalogue page URL."""

    soup = BeautifulSoup(html, "html.parser")
    records: list[BookRecord] = []

    for index, article in enumerate(soup.select("article.product_pod"), start=1):
        if not isinstance(article, Tag):
            continue
        try:
            link = _required_tag(article, "h3 a", "product link")
            title = clean_text(link.get("title") or link.get_text(" ", strip=True))
            if not title:
                raise ValueError("Book title was empty")

            price_tag = _required_tag(article, ".price_color", "price")
            availability_tag = _required_tag(article, ".availability", "availability")
            rating_tag = _required_tag(article, "p.star-rating", "rating")
            image_tag = _required_tag(article, "img", "image")

            records.append(
                BookRecord(
                    title=title,
                    price_gbp=clean_price(price_tag.get_text(" ", strip=True)),
                    availability=clean_availability(
                        availability_tag.get_text(" ", strip=True)
                    ),
                    rating=clean_rating(rating_tag.get("class", [])),
                    product_url=absolute_url(source_url, link.get("href")),
                    image_url=absolute_url(source_url, image_tag.get("src")),
                    source_url=source_url,
                )
            )
        except (TypeError, ValueError) as exc:
            LOGGER.warning("Skipping malformed book card %s on %s: %s", index, source_url, exc)

    next_link = soup.select_one("li.next a")
    next_url = None
    if isinstance(next_link, Tag) and next_link.get("href"):
        next_url = absolute_url(source_url, next_link.get("href"))

    return ParsedPage(records=records, next_url=next_url)
