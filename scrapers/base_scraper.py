"""Abstract base scraper with retry logic and session management."""

import logging
import time
from abc import ABC, abstractmethod
from typing import List, Optional

import requests
from bs4 import BeautifulSoup

from data_schema import JobPosting
import config

logger = logging.getLogger(__name__)


class BaseScraper(ABC):
    """Base class for all job portal scrapers."""

    def __init__(self, name: str):
        self.name = name
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": config.USER_AGENT,
            "Accept-Language": "es-CO,es;q=0.9,en;q=0.8",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        })

    # ── Network helpers ───────────────────────────────────────────
    def fetch(self, url: str, **kwargs) -> Optional[BeautifulSoup]:
        """Fetch a URL with retry + exponential backoff. Returns parsed soup."""
        for attempt in range(config.RETRY_ATTEMPTS):
            try:
                resp = self.session.get(url, timeout=config.REQUEST_TIMEOUT, **kwargs)
                resp.raise_for_status()
                return BeautifulSoup(resp.content, "lxml")
            except requests.RequestException as exc:
                wait = 2 ** attempt
                logger.warning(
                    "%s  attempt %d/%d for %s failed: %s  (retry in %ds)",
                    self.name, attempt + 1, config.RETRY_ATTEMPTS, url, exc, wait,
                )
                if attempt < config.RETRY_ATTEMPTS - 1:
                    time.sleep(wait)
        logger.error("%s  gave up on %s", self.name, url)
        return None

    def fetch_json(self, url: str, **kwargs) -> Optional[dict]:
        """Fetch a URL expecting JSON response."""
        for attempt in range(config.RETRY_ATTEMPTS):
            try:
                resp = self.session.get(url, timeout=config.REQUEST_TIMEOUT, **kwargs)
                resp.raise_for_status()
                return resp.json()
            except (requests.RequestException, ValueError) as exc:
                wait = 2 ** attempt
                logger.warning(
                    "%s  attempt %d/%d JSON fetch %s failed: %s",
                    self.name, attempt + 1, config.RETRY_ATTEMPTS, url, exc,
                )
                if attempt < config.RETRY_ATTEMPTS - 1:
                    time.sleep(wait)
        return None

    # ── Abstract interface ────────────────────────────────────────
    @abstractmethod
    def get_urls(self) -> List[str]:
        """Return list of page URLs to scrape (handles pagination)."""

    @abstractmethod
    def parse_listings(self, soup: BeautifulSoup, url: str) -> List[JobPosting]:
        """Parse all job listings from a single page."""

    # ── Main runner ───────────────────────────────────────────────
    def run(self) -> List[JobPosting]:
        """Execute the full scraping workflow for this portal."""
        all_jobs: List[JobPosting] = []
        urls = self.get_urls()
        logger.info("%s  scraping %d URL(s)", self.name, len(urls))

        for i, url in enumerate(urls):
            soup = self.fetch(url)
            if soup is None:
                continue

            jobs = self.parse_listings(soup, url)
            all_jobs.extend(jobs)
            logger.info(
                "%s  page %d/%d  →  %d jobs (total %d)",
                self.name, i + 1, len(urls), len(jobs), len(all_jobs),
            )

            # Stop paginating when a page returns nothing
            if not jobs and i > 0:
                logger.info("%s  empty page, stopping pagination", self.name)
                break

            if i < len(urls) - 1:
                time.sleep(config.POLITE_DELAY)

        logger.info("%s  finished: %d jobs total", self.name, len(all_jobs))
        return all_jobs

    # ── Helpers ───────────────────────────────────────────────────
    @staticmethod
    def clean_text(text: Optional[str]) -> str:
        """Collapse whitespace and strip."""
        if not text:
            return ""
        return " ".join(text.split()).strip()
