import pytest

from scraper.cleaner import (
    absolute_url,
    clean_availability,
    clean_price,
    clean_rating,
    clean_text,
)


def test_clean_text_collapses_whitespace() -> None:
    assert clean_text("  A\n useful\t title  ") == "A useful title"


def test_clean_price_returns_float() -> None:
    assert clean_price("£51.77") == 51.77


def test_clean_price_rejects_missing_number() -> None:
    with pytest.raises(ValueError):
        clean_price("price unavailable")


def test_clean_availability_normalises_known_values() -> None:
    assert clean_availability("\n In stock \n") == "in_stock"
    assert clean_availability("Out of stock") == "out_of_stock"
    assert clean_availability("Back ordered") == "unknown"


def test_clean_rating_uses_star_class() -> None:
    assert clean_rating(["star-rating", "Three"]) == 3
    assert clean_rating(["star-rating"]) == 0


def test_absolute_url_resolves_relative_path() -> None:
    assert (
        absolute_url(
            "https://books.toscrape.com/catalogue/page-2.html",
            "a-light-in-the-attic_1000/index.html",
        )
        == "https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html"
    )
