# The Polite Scraper

A small Python scraper that follows the professional scraping pipeline:

`fetch → parse → extract → clean → structure → save`

The default target is [Books to Scrape](https://books.toscrape.com/), a website created for scraping practice. The program collects book listing data and writes one structured JSON object per line to `data/records.jsonl`.

## Collected fields

Each record contains:

- `title`
- `price_gbp`
- `availability`
- `rating`
- `product_url`
- `image_url`
- `source_url`

Example:

```json
{"title":"A Light in the Attic","price_gbp":51.77,"availability":"in_stock","rating":3,"product_url":"https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html","image_url":"https://books.toscrape.com/media/cache/example.jpg","source_url":"https://books.toscrape.com/"}
```

## Responsible scraping behaviour

The scraper:

- requests and parses `/robots.txt` before scraping;
- refuses to fetch a URL disallowed by `robots.txt`;
- stops if robots policy cannot be retrieved, rather than guessing;
- identifies itself with an honest `User-Agent`;
- remains on the configured host;
- waits at least 1.5 seconds between requests;
- honours a longer `Crawl-delay` when one is published;
- uses timeouts, retries and exponential backoff;
- honours `Retry-After` for temporary server responses where possible;
- logs malformed records and skips them instead of saving misleading data;
- deduplicates books by product URL.

A `404` response for `/robots.txt` is treated as no published restrictions. Other robots retrieval failures stop the run.

## Project structure

```text
polite_scraper/
├── data/
│   └── records.jsonl
├── scraper/
│   ├── __init__.py
│   ├── cleaner.py
│   ├── config.py
│   ├── fetcher.py
│   ├── models.py
│   └── parser.py
├── tests/
│   ├── test_cleaner.py
│   └── test_parser.py
├── .gitignore
├── main.py
├── README.md
└── requirements.txt
```

## Setup

### Windows PowerShell

```powershell
cd polite_scraper
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### macOS or Linux

```bash
cd polite_scraper
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## Run the scraper

The safe default scrapes five catalogue pages:

```bash
python main.py
```

Scrape only one page while testing:

```bash
python main.py --max-pages 1
```

Scrape every catalogue page:

```bash
python main.py --max-pages 0
```

Choose a different output path or a slower delay:

```bash
python main.py --output data/books.jsonl --delay 2.5
```

## Run the tests

```bash
pytest -q
```

The tests use local HTML and do not send requests to the live website.

## Configuration

The defaults can be overridden with environment variables:

| Variable | Default |
|---|---|
| `SCRAPER_BASE_URL` | `https://books.toscrape.com/` |
| `SCRAPER_START_URL` | `https://books.toscrape.com/` |
| `SCRAPER_USER_AGENT` | `FlyRankPoliteScraper/1.0 (+mailto:shyampopat2023@gmail.com)` |
| `SCRAPER_DELAY_SECONDS` | `1.5` |
| `SCRAPER_TIMEOUT_SECONDS` | `15` |
| `SCRAPER_MAX_RETRIES` | `3` |
| `SCRAPER_OUTPUT_PATH` | `data/records.jsonl` |

## Limitations

- The parser is intentionally written for the HTML structure of Books to Scrape.
- It extracts catalogue-card data, not the longer description on each individual product page.
- It does not execute JavaScript.
- A new target site requires new selectors and should only be used after checking that site's terms and robots policy.

## Submission

Submit the public GitHub repository URL in FlyRank. Suggested reviewer notes:

> Built a Python scraper that checks robots.txt before fetching, uses an identifiable User-Agent, applies a configurable request delay, retries temporary failures, extracts and cleans book data, deduplicates records, and saves JSONL suitable for a later RAG pipeline. Parsing and cleaning are separated from networking and covered by unit tests using local HTML.
