from scraper.parser import parse_listing_page


SAMPLE_HTML = """
<html>
  <body>
    <article class="product_pod">
      <div class="image_container">
        <a href="a-light-in-the-attic_1000/index.html">
          <img src="../media/cache/book.jpg" alt="A Light in the Attic">
        </a>
      </div>
      <p class="star-rating Three"><i class="icon-star"></i></p>
      <h3><a href="a-light-in-the-attic_1000/index.html"
             title="A Light in the Attic">A Light in...</a></h3>
      <div class="product_price">
        <p class="price_color">£51.77</p>
        <p class="instock availability">\n In stock\n</p>
      </div>
    </article>
    <ul class="pager">
      <li class="next"><a href="page-2.html">next</a></li>
    </ul>
  </body>
</html>
"""


def test_parse_listing_page_extracts_clean_record_and_next_url() -> None:
    source_url = "https://books.toscrape.com/catalogue/page-1.html"
    parsed = parse_listing_page(SAMPLE_HTML, source_url)

    assert len(parsed.records) == 1
    record = parsed.records[0]
    assert record.title == "A Light in the Attic"
    assert record.price_gbp == 51.77
    assert record.availability == "in_stock"
    assert record.rating == 3
    assert record.product_url == (
        "https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html"
    )
    assert record.image_url == "https://books.toscrape.com/media/cache/book.jpg"
    assert record.source_url == source_url
    assert parsed.next_url == "https://books.toscrape.com/catalogue/page-2.html"


def test_parser_skips_malformed_card_instead_of_creating_bad_record() -> None:
    parsed = parse_listing_page(
        '<article class="product_pod"><h3>No link</h3></article>',
        "https://books.toscrape.com/",
    )
    assert parsed.records == []
