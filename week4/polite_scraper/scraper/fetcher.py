"""Responsible HTTP fetching with robots.txt checks and rate limiting."""

from __future__ import annotations

import logging
import time
import urllib.robotparser
from dataclasses import dataclass
from email.utils import parsedate_to_datetime
from urllib.parse import urljoin, urlparse

import requests

LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class RobotsPolicy:
    parser: urllib.robotparser.RobotFileParser
    crawl_delay_seconds: float | None
    robots_url: str


class PoliteFetcher:
    """Fetch pages while identifying the bot and respecting site policy."""

    def __init__(
        self,
        *,
        base_url: str,
        user_agent: str,
        request_delay_seconds: float = 1.5,
        timeout_seconds: float = 15.0,
        max_retries: int = 3,
        session: requests.Session | None = None,
    ) -> None:
        if request_delay_seconds < 0:
            raise ValueError("request_delay_seconds cannot be negative")
        if max_retries < 1:
            raise ValueError("max_retries must be at least 1")

        self.base_url = base_url
        self.user_agent = user_agent
        self.request_delay_seconds = request_delay_seconds
        self.timeout_seconds = timeout_seconds
        self.max_retries = max_retries
        self.session = session or requests.Session()
        self.session.headers.update(
            {
                "User-Agent": user_agent,
                "Accept": "text/html,application/xhtml+xml",
            }
        )
        self._last_request_at: float | None = None
        self._base_host = urlparse(base_url).netloc
        self._robots_policy = self._load_robots_policy()

    def __enter__(self) -> "PoliteFetcher":
        return self

    def __exit__(self, *_: object) -> None:
        self.close()

    def close(self) -> None:
        self.session.close()

    def _load_robots_policy(self) -> RobotsPolicy:
        robots_url = urljoin(self.base_url, "/robots.txt")
        parser = urllib.robotparser.RobotFileParser()
        parser.set_url(robots_url)

        try:
            response = self.session.get(robots_url, timeout=self.timeout_seconds)
        except requests.RequestException as exc:
            raise RuntimeError(
                f"Could not retrieve {robots_url}; stopping rather than guessing permission"
            ) from exc

        if response.status_code == 404:
            # No robots file exists, so there are no published restrictions.
            parser.parse([])
            LOGGER.info("No robots.txt was published at %s", robots_url)
        else:
            response.raise_for_status()
            parser.parse(response.text.splitlines())
            LOGGER.info("Loaded robots policy from %s", robots_url)

        crawl_delay = parser.crawl_delay(self.user_agent)
        if crawl_delay is None:
            crawl_delay = parser.crawl_delay("*")

        return RobotsPolicy(
            parser=parser,
            crawl_delay_seconds=float(crawl_delay) if crawl_delay is not None else None,
            robots_url=robots_url,
        )

    @property
    def effective_delay_seconds(self) -> float:
        """Use at least the configured delay and any robots crawl delay."""

        robots_delay = self._robots_policy.crawl_delay_seconds or 0.0
        return max(self.request_delay_seconds, robots_delay)

    def can_fetch(self, url: str) -> bool:
        return self._robots_policy.parser.can_fetch(self.user_agent, url)

    def _validate_target(self, url: str) -> None:
        parsed = urlparse(url)
        if parsed.scheme not in {"http", "https"}:
            raise ValueError(f"Unsupported URL scheme: {url}")
        if parsed.netloc != self._base_host:
            raise ValueError(f"Refusing to leave allowed host {self._base_host}: {url}")
        if not self.can_fetch(url):
            raise PermissionError(
                f"robots.txt at {self._robots_policy.robots_url} disallows {url}"
            )

    def _wait_for_rate_limit(self) -> None:
        if self._last_request_at is None:
            return
        elapsed = time.monotonic() - self._last_request_at
        remaining = self.effective_delay_seconds - elapsed
        if remaining > 0:
            time.sleep(remaining)

    @staticmethod
    def _retry_after_seconds(response: requests.Response) -> float | None:
        value = response.headers.get("Retry-After")
        if not value:
            return None
        try:
            return max(0.0, float(value))
        except ValueError:
            try:
                retry_at = parsedate_to_datetime(value)
                now = parsedate_to_datetime(response.headers["Date"])
                return max(0.0, (retry_at - now).total_seconds())
            except (KeyError, TypeError, ValueError, OverflowError):
                return None

    def fetch(self, url: str) -> str:
        """Return HTML for one allowed page, retrying transient failures."""

        self._validate_target(url)
        last_error: Exception | None = None

        for attempt in range(1, self.max_retries + 1):
            self._wait_for_rate_limit()
            try:
                LOGGER.info("GET %s (attempt %s/%s)", url, attempt, self.max_retries)
                response = self.session.get(url, timeout=self.timeout_seconds)
                self._last_request_at = time.monotonic()

                if response.status_code in {429, 500, 502, 503, 504}:
                    retry_after = self._retry_after_seconds(response)
                    delay = retry_after if retry_after is not None else 2 ** (attempt - 1)
                    if attempt < self.max_retries:
                        LOGGER.warning(
                            "Temporary HTTP %s from %s; retrying in %.1fs",
                            response.status_code,
                            url,
                            delay,
                        )
                        time.sleep(delay)
                        continue

                response.raise_for_status()
                return response.text
            except (requests.Timeout, requests.ConnectionError, requests.HTTPError) as exc:
                last_error = exc
                if attempt == self.max_retries:
                    break
                delay = 2 ** (attempt - 1)
                LOGGER.warning("Fetch failed for %s: %s; retrying in %.1fs", url, exc, delay)
                time.sleep(delay)

        raise RuntimeError(f"Failed to fetch {url} after {self.max_retries} attempts") from last_error
