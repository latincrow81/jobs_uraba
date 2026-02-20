"""Scraper for co.computrabajo.com — one of Colombia's largest job boards."""

import re
import logging
from typing import List
from bs4 import BeautifulSoup

from data_schema import JobPosting
from .base_scraper import BaseScraper

logger = logging.getLogger(__name__)

# Locations to search on Computrabajo
_LOCATIONS = [
    ("apartado", "Apartadó"),
    ("turbo-antioquia", "Turbo"),
    ("carepa", "Carepa"),
    ("chigorodo", "Chigorodó"),
]

MAX_PAGES = 5


class ComputrabajoScraper(BaseScraper):
    def __init__(self):
        super().__init__("Computrabajo")

    def get_urls(self) -> List[str]:
        urls = []
        for slug, _ in _LOCATIONS:
            for page in range(1, MAX_PAGES + 1):
                urls.append(
                    f"https://co.computrabajo.com/empleos-en-{slug}?p={page}"
                )
        return urls

    def parse_listings(self, soup: BeautifulSoup, url: str) -> List[JobPosting]:
        jobs: List[JobPosting] = []

        # Computrabajo uses <article> or <div> with class containing "box_offer"
        containers = soup.select("article.box_offer") or soup.select("div.box_offer")
        if not containers:
            # Fallback: look for any link pattern
            containers = soup.select("div.bRS") or soup.select("div[class*='offer']")

        for el in containers:
            try:
                job = self._parse_one(el, url)
                if job:
                    jobs.append(job)
            except Exception as exc:
                logger.debug("Computrabajo parse error: %s", exc)

        return jobs

    def _parse_one(self, el, page_url: str) -> JobPosting | None:
        # Title + link
        link_el = (
            el.select_one("a[href*='/oferta-de-trabajo']")
            or el.select_one("h2 a")
            or el.select_one("a.js-o-link")
        )
        if not link_el:
            return None
        title = self.clean_text(link_el.get_text())
        href = link_el.get("href", "")
        job_url = href if href.startswith("http") else f"https://co.computrabajo.com{href}"

        # Company
        company_el = el.select_one("a[class*='enterprise']") or el.select_one("span.icon-li-icon")
        company = self.clean_text(company_el.get_text()) if company_el else "N/A"
        if not company or company == "N/A":
            # Try alternative
            for span in el.select("span"):
                t = self.clean_text(span.get_text())
                if t and t != title and len(t) < 80:
                    company = t
                    break

        # Location
        loc_el = el.select_one("span[class*='location']") or el.select_one("p[class*='city']")
        location = self.clean_text(loc_el.get_text()) if loc_el else ""
        if not location:
            # Extract from URL
            if "apartado" in page_url:
                location = "Apartadó, Antioquia"
            elif "turbo" in page_url:
                location = "Turbo, Antioquia"
            elif "carepa" in page_url:
                location = "Carepa, Antioquia"
            elif "chigorodo" in page_url:
                location = "Chigorodó, Antioquia"

        # Salary
        salary_el = el.select_one("span[class*='salary']") or el.select_one("p[class*='salary']")
        salary = self.clean_text(salary_el.get_text()) if salary_el else ""

        # Date
        date_el = el.select_one("span[class*='date']") or el.select_one("p[class*='date']")
        date_posted = self.clean_text(date_el.get_text()) if date_el else None

        if not title:
            return None

        return JobPosting(
            title=title,
            company=company,
            location=location,
            salary_raw=salary,
            url=job_url,
            source="Computrabajo",
            date_posted=date_posted,
        )
