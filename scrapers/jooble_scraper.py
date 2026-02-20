"""Scraper for co.jooble.org — job aggregator."""

import logging
import json
from typing import List
from bs4 import BeautifulSoup

from data_schema import JobPosting
from .base_scraper import BaseScraper

logger = logging.getLogger(__name__)

MAX_PAGES = 5


class JoobleScraper(BaseScraper):
    def __init__(self):
        super().__init__("Jooble")

    def get_urls(self) -> List[str]:
        urls = []
        for page in range(1, MAX_PAGES + 1):
            urls.append(
                f"https://co.jooble.org/trabajo/Urabá,-Antioquia?p={page}"
            )
        # Also search Apartadó specifically
        for page in range(1, 3):
            urls.append(
                f"https://co.jooble.org/trabajo/Apartadó,-Antioquia?p={page}"
            )
        return urls

    def parse_listings(self, soup: BeautifulSoup, url: str) -> List[JobPosting]:
        jobs: List[JobPosting] = []

        # Jooble may embed data as JSON
        for script in soup.select("script[type='application/ld+json']"):
            try:
                data = json.loads(script.string or "")
                items = data if isinstance(data, list) else [data]
                for item in items:
                    if isinstance(item, dict) and item.get("@type") == "JobPosting":
                        jobs.append(self._from_jsonld(item))
            except (json.JSONDecodeError, Exception):
                pass

        # HTML card fallback — Jooble uses various card structures
        containers = (
            soup.select("article[data-test-name='vacancy']")
            or soup.select("div[class*='vacancy']")
            or soup.select("div[data-test-name]")
            or soup.select("article")
        )

        for el in containers:
            try:
                job = self._parse_card(el, url)
                if job:
                    jobs.append(job)
            except Exception as exc:
                logger.debug("Jooble card parse error: %s", exc)

        return jobs

    def _from_jsonld(self, data: dict) -> JobPosting:
        title = data.get("title", "")
        org = data.get("hiringOrganization", {})
        company = org.get("name", "") if isinstance(org, dict) else ""

        loc = data.get("jobLocation", {})
        location = ""
        if isinstance(loc, dict):
            addr = loc.get("address", {})
            if isinstance(addr, dict):
                location = addr.get("addressLocality", "")
        elif isinstance(loc, list) and loc:
            addr = loc[0].get("address", {})
            if isinstance(addr, dict):
                location = addr.get("addressLocality", "")

        salary_raw = ""
        base = data.get("baseSalary", {})
        if isinstance(base, dict):
            val = base.get("value", {})
            if isinstance(val, dict):
                salary_raw = f"{val.get('minValue', '')} - {val.get('maxValue', '')} {base.get('currency', 'COP')}"

        return JobPosting(
            title=title,
            company=company,
            location=location,
            salary_raw=salary_raw,
            description=data.get("description", "")[:500],
            url=data.get("url", ""),
            source="Jooble",
            date_posted=data.get("datePosted"),
        )

    def _parse_card(self, el, page_url: str) -> JobPosting | None:
        # Title + link
        title_el = (
            el.select_one("header a")
            or el.select_one("a[class*='title']")
            or el.select_one("h2 a")
            or el.select_one("a")
        )
        if not title_el:
            return None

        title = self.clean_text(title_el.get_text())
        href = title_el.get("href", "")
        job_url = href if href.startswith("http") else f"https://co.jooble.org{href}"

        if not title or len(title) < 3:
            return None

        # Company
        company_el = el.select_one("p[class*='company']") or el.select_one("span[class*='company']")
        company = self.clean_text(company_el.get_text()) if company_el else "N/A"

        # Location
        loc_el = el.select_one("span[class*='location']") or el.select_one("div[class*='location']")
        location = self.clean_text(loc_el.get_text()) if loc_el else "Urabá, Antioquia"

        # Salary
        sal_el = el.select_one("span[class*='salary']") or el.select_one("div[class*='salary']")
        salary = self.clean_text(sal_el.get_text()) if sal_el else ""

        # Snippet / description
        desc_el = el.select_one("div[class*='description']") or el.select_one("span[class*='snippet']")
        description = self.clean_text(desc_el.get_text())[:300] if desc_el else ""

        return JobPosting(
            title=title,
            company=company,
            location=location,
            salary_raw=salary,
            description=description,
            url=job_url,
            source="Jooble",
        )
