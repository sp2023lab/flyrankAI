"""Command-line entry point for the polite scraper."""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

from scraper.config import DEFAULT_SETTINGS
from scraper.fetcher import PoliteFetcher
from scraper.models import BookRecord
from scraper.parser import parse_listing_page

LOGGER = logging.getLogger(__name__)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Politely scrape structured book records from Books to Scrape."
    )
    parser.add_argument("--start-url", default=DEFAULT_SETTINGS.start_url)
    parser.add_argument("--output", type=Path, default=DEFAULT_SETTINGS.output_path)
    parser.add_argument(
        "--max-pages",
        type=int,
        default=5,
        help="Maximum catalogue pages to scrape. Use 0 for every available page.",
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=DEFAULT_SETTINGS.request_delay_seconds,
        help="Minimum delay between page requests in seconds.",
    )
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
    )
    return parser.parse_args()


def write_jsonl(records: list[BookRecord], output_path: Path) -> None:
    """Atomically replace the output file with newline-delimited JSON."""

    output_path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path = output_path.with_suffix(output_path.suffix + ".tmp")

    with temporary_path.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record.to_dict(), ensure_ascii=False) + "\n")

    temporary_path.replace(output_path)


def scrape(start_url: str, max_pages: int, delay: float) -> list[BookRecord]:
    if max_pages < 0:
        raise ValueError("max_pages cannot be negative")

    records_by_url: dict[str, BookRecord] = {}
    current_url: str | None = start_url
    page_number = 0

    with PoliteFetcher(
        base_url=DEFAULT_SETTINGS.base_url,
        user_agent=DEFAULT_SETTINGS.user_agent,
        request_delay_seconds=delay,
        timeout_seconds=DEFAULT_SETTINGS.timeout_seconds,
        max_retries=DEFAULT_SETTINGS.max_retries,
    ) as fetcher:
        while current_url and (max_pages == 0 or page_number < max_pages):
            page_number += 1
            LOGGER.info("Scraping page %s: %s", page_number, current_url)

            try:
                html = fetcher.fetch(current_url)
                parsed = parse_listing_page(html, current_url)
            except (PermissionError, RuntimeError, ValueError) as exc:
                LOGGER.error("Stopping at %s: %s", current_url, exc)
                break

            for record in parsed.records:
                records_by_url[record.product_url] = record

            LOGGER.info(
                "Page %s produced %s records (%s unique total)",
                page_number,
                len(parsed.records),
                len(records_by_url),
            )
            current_url = parsed.next_url

    return list(records_by_url.values())


def main() -> int:
    args = parse_args()
    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )

    try:
        records = scrape(args.start_url, args.max_pages, args.delay)
        write_jsonl(records, args.output)
    except (OSError, ValueError) as exc:
        LOGGER.error("Scraper failed: %s", exc)
        return 1

    LOGGER.info("Saved %s records to %s", len(records), args.output)
    return 0


if __name__ == "__main__":
    sys.exit(main())
