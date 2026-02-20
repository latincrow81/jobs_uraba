"""Scraper for co.indeed.com — may be JS-rendered, handles gracefully."""

import logging
import re
from typing import List
from bs4 import BeautifulSoup

from data_schema import JobPosting
from .base_scraper import BaseScraper

logger = logging.getLogger(__name__)

MAX_PAGES = 5


class IndeedScraper(BaseScraper):
    def __init__(self):
        super().__init__("Indeed")

    def get_urls(self) -> List[str]:
        # Indeed search for Urabá + Apartadó
        base = "https://co.indeed.com/jobs"
        urls = []
        for query in ["Urabá", "Apartadó Antioquia"]:
            for start in range(0, MAX_PAGES * 10, 10):
                urls.append(f"{base}?q=&l={query}&start={start}")
        return urls

    def parse_listings(self, soup: BeautifulSoup, url: str) -> List[JobPosting]:
        jobs: List[JobPosting] = []

        # Indeed primary card selector
        containers = soup.select("div.job_seen_beacon") or soup.select("div.jobsearch-ResultsList > div")
        if not containers:
            # Try alternative selectors
            containers = soup.select("td.resultContent") or soup.select("div[data-jk]")

        for el in containers:
            try:
                job = self._parse_one(el)
                if job:
                    jobs.append(job)
            except Exception as exc:
                logger.debug("Indeed parse error: %s", exc)

        # Indeed often serves JS-rendered content; if we got nothing, log it
        if not jobs:
            logger.warning("Indeed returned 0 jobs for %s (likely JS-rendered)", url)

        return jobs

    def _parse_one(self, el) -> JobPosting | None:
        # Title
        title_el = (
            el.select_one("h2.jobTitle a span")
            or el.select_one("h2 a")
            or el.select_one("a[data-jk]")
        )
        if not title_el:
            return None
        title = self.clean_text(title_el.get_text())

        # URL
        link = el.select_one("h2 a") or el.select_one("a[data-jk]")
        href = link.get("href", "") if link else ""
        job_url = href if href.startswith("http") else f"https://co.indeed.com{href}"

        # Company
        company_el = el.select_one("span[data-testid='company-name']") or el.select_one("span.companyName")
        company = self.clean_text(company_el.get_text()) if company_el else "N/A"

        # Location
        loc_el = el.select_one("div[data-testid='text-location']") or el.select_one("div.companyLocation")
        location = self.clean_text(loc_el.get_text()) if loc_el else ""

        # Salary
        sal_el = el.select_one("div.salary-snippet-container") or el.select_one("span.estimated-salary")
        salary = self.clean_text(sal_el.get_text()) if sal_el else ""

        if not title:
            return None

        return JobPosting(
            title=title,
            company=company,
            location=location,
            salary_raw=salary,
            url=job_url,
            source="Indeed",
        )
