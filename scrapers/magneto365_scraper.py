"""Scraper for magneto365.com — Colombian job platform with API-like structure."""

import logging
import json
from typing import List
from bs4 import BeautifulSoup

from data_schema import JobPosting
from .base_scraper import BaseScraper

logger = logging.getLogger(__name__)

_LOCATIONS = [
    ("apartado", "Apartadó"),
    ("turbo", "Turbo"),
    ("carepa", "Carepa"),
    ("chigorodo", "Chigorodó"),
]
MAX_PAGES = 3


class Magneto365Scraper(BaseScraper):
    def __init__(self):
        super().__init__("Magneto365")

    def get_urls(self) -> List[str]:
        urls = []
        for slug, _ in _LOCATIONS:
            for page in range(1, MAX_PAGES + 1):
                urls.append(
                    f"https://www.magneto365.com/co/trabajos/ofertas-empleo-en-{slug}?page={page}"
                )
        return urls

    def parse_listings(self, soup: BeautifulSoup, url: str) -> List[JobPosting]:
        jobs: List[JobPosting] = []

        # Magneto365 may embed job data as JSON in script tags
        for script in soup.select("script[type='application/ld+json']"):
            try:
                data = json.loads(script.string or "")
                if isinstance(data, dict) and data.get("@type") == "JobPosting":
                    jobs.append(self._from_jsonld(data))
                elif isinstance(data, list):
                    for item in data:
                        if isinstance(item, dict) and item.get("@type") == "JobPosting":
                            jobs.append(self._from_jsonld(item))
            except (json.JSONDecodeError, Exception) as exc:
                logger.debug("Magneto365 JSON-LD parse error: %s", exc)

        # Also try HTML card selectors
        containers = (
            soup.select("div[class*='job-card']")
            or soup.select("a[class*='offer']")
            or soup.select("div[class*='vacancy']")
        )
        for el in containers:
            try:
                job = self._parse_card(el, url)
                if job:
                    jobs.append(job)
            except Exception as exc:
                logger.debug("Magneto365 card parse error: %s", exc)

        return jobs

    def _from_jsonld(self, data: dict) -> JobPosting:
        """Parse structured JSON-LD job posting."""
        title = data.get("title", "")
        company = ""
        org = data.get("hiringOrganization", {})
        if isinstance(org, dict):
            company = org.get("name", "")

        location = ""
        loc = data.get("jobLocation", {})
        if isinstance(loc, dict):
            addr = loc.get("address", {})
            if isinstance(addr, dict):
                location = addr.get("addressLocality", "")

        salary = ""
        base_salary = data.get("baseSalary", {})
        if isinstance(base_salary, dict):
            val = base_salary.get("value", {})
            if isinstance(val, dict):
                salary = f"{val.get('minValue', '')} - {val.get('maxValue', '')} {val.get('unitText', '')}"

        return JobPosting(
            title=title,
            company=company,
            location=location,
            salary_raw=salary,
            description=data.get("description", "")[:500],
            url=data.get("url", ""),
            source="Magneto365",
            date_posted=data.get("datePosted", None),
        )

    def _parse_card(self, el, page_url: str) -> JobPosting | None:
        link_el = el.select_one("a") or el
        if link_el.name == "a":
            href = link_el.get("href", "")
        else:
            link_el = el.select_one("a")
            href = link_el.get("href", "") if link_el else ""

        title_el = el.select_one("h2") or el.select_one("h3") or el.select_one("span[class*='title']")
        title = self.clean_text(title_el.get_text()) if title_el else self.clean_text(el.get_text())

        if not title or len(title) < 3:
            return None

        job_url = href if href.startswith("http") else f"https://www.magneto365.com{href}"

        company_el = el.select_one("span[class*='company']") or el.select_one("p[class*='company']")
        company = self.clean_text(company_el.get_text()) if company_el else "N/A"

        loc_el = el.select_one("span[class*='location']") or el.select_one("span[class*='city']")
        location = self.clean_text(loc_el.get_text()) if loc_el else ""

        return JobPosting(
            title=title,
            company=company,
            location=location,
            url=job_url,
            source="Magneto365",
        )
