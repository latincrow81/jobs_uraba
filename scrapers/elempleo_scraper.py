"""Scraper for elempleo.com — major Colombian job portal."""

import logging
from typing import List
from bs4 import BeautifulSoup

from data_schema import JobPosting
from .base_scraper import BaseScraper

logger = logging.getLogger(__name__)

_LOCATIONS = [
    "apartado",
    "turbo",
    "carepa",
    "chigorodo",
]
MAX_PAGES = 3


class ElempleoScraper(BaseScraper):
    def __init__(self):
        super().__init__("elempleo.com")

    def get_urls(self) -> List[str]:
        urls = []
        for loc in _LOCATIONS:
            for page in range(1, MAX_PAGES + 1):
                urls.append(
                    f"https://www.elempleo.com/co/ofertas-empleo/trabajo-{loc}/pagina/{page}"
                )
        return urls

    def parse_listings(self, soup: BeautifulSoup, url: str) -> List[JobPosting]:
        jobs: List[JobPosting] = []

        # elempleo uses various card selectors
        containers = (
            soup.select("div.result-item")
            or soup.select("li.list-item")
            or soup.select("div[class*='offer-card']")
            or soup.select("a[class*='offer']")
        )

        for el in containers:
            try:
                job = self._parse_one(el, url)
                if job:
                    jobs.append(job)
            except Exception as exc:
                logger.debug("elempleo parse error: %s", exc)

        return jobs

    def _parse_one(self, el, page_url: str) -> JobPosting | None:
        # Title
        title_el = (
            el.select_one("h2 a")
            or el.select_one("a[class*='title']")
            or el.select_one("h3 a")
            or el.select_one("a")
        )
        if not title_el:
            return None
        title = self.clean_text(title_el.get_text())
        href = title_el.get("href", "")
        job_url = href if href.startswith("http") else f"https://www.elempleo.com{href}"

        # Company
        company_el = el.select_one("span[class*='company']") or el.select_one("p[class*='company']")
        company = self.clean_text(company_el.get_text()) if company_el else "N/A"

        # Location
        loc_el = el.select_one("span[class*='location']") or el.select_one("span[class*='city']")
        location = self.clean_text(loc_el.get_text()) if loc_el else ""
        if not location:
            # Infer from URL
            for loc in _LOCATIONS:
                if loc in page_url:
                    location = f"{loc.title()}, Antioquia"
                    break

        # Salary
        sal_el = el.select_one("span[class*='salary']") or el.select_one("span[class*='wage']")
        salary = self.clean_text(sal_el.get_text()) if sal_el else ""

        if not title or len(title) < 3:
            return None

        return JobPosting(
            title=title,
            company=company,
            location=location,
            salary_raw=salary,
            url=job_url,
            source="elempleo.com",
        )
