"""Scraper for comfama.com — Urabá regional employment service."""

import logging
import json
import re
from typing import List
from bs4 import BeautifulSoup

from data_schema import JobPosting
from .base_scraper import BaseScraper

logger = logging.getLogger(__name__)

_URLS = [
    "https://www.comfama.com/servicio-de-empleo/personas/vacantes-en-antioquia/uraba/",
    "https://www.comfama.com/servicio-de-empleo/personas/vacantes-en-antioquia/uraba/apartado/",
    "https://www.comfama.com/servicio-de-empleo/personas/vacantes-en-antioquia/uraba/turbo/",
    "https://www.comfama.com/servicio-de-empleo/personas/vacantes-en-antioquia/uraba/carepa/",
    "https://www.comfama.com/servicio-de-empleo/personas/vacantes-en-antioquia/uraba/chigorodo/",
]


class ComfamaScraper(BaseScraper):
    def __init__(self):
        super().__init__("Comfama")

    def get_urls(self) -> List[str]:
        return _URLS

    def parse_listings(self, soup: BeautifulSoup, url: str) -> List[JobPosting]:
        jobs: List[JobPosting] = []

        # Try JSON-LD first
        for script in soup.select("script[type='application/ld+json']"):
            try:
                data = json.loads(script.string or "")
                if isinstance(data, list):
                    for item in data:
                        if isinstance(item, dict) and item.get("@type") == "JobPosting":
                            jobs.append(self._from_jsonld(item))
                elif isinstance(data, dict) and data.get("@type") == "JobPosting":
                    jobs.append(self._from_jsonld(data))
            except (json.JSONDecodeError, Exception):
                pass

        # Try embedded JSON data in script tags (Comfama may use Next.js/React)
        for script in soup.select("script"):
            text = script.string or ""
            if "vacantes" in text.lower() or "ofertas" in text.lower():
                try:
                    # Look for JSON arrays in script content
                    matches = re.findall(r'\[{.*?"titulo".*?}\]', text, re.DOTALL)
                    for match in matches:
                        data = json.loads(match)
                        for item in data:
                            job = self._from_comfama_json(item)
                            if job:
                                jobs.append(job)
                except (json.JSONDecodeError, Exception):
                    pass

        # HTML card fallback
        containers = (
            soup.select("div[class*='vacancy']")
            or soup.select("div[class*='card']")
            or soup.select("article")
            or soup.select("li[class*='offer']")
        )
        for el in containers:
            try:
                job = self._parse_card(el, url)
                if job:
                    jobs.append(job)
            except Exception as exc:
                logger.debug("Comfama card parse error: %s", exc)

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

        return JobPosting(
            title=title,
            company=company or "Comfama",
            location=location,
            description=data.get("description", "")[:500],
            url=data.get("url", ""),
            source="Comfama",
            date_posted=data.get("datePosted"),
        )

    def _from_comfama_json(self, item: dict) -> JobPosting | None:
        title = item.get("titulo") or item.get("title") or item.get("nombre", "")
        if not title:
            return None
        return JobPosting(
            title=title,
            company=item.get("empresa", "Comfama"),
            location=item.get("ubicacion", item.get("ciudad", "")),
            salary_raw=item.get("salario", ""),
            url=item.get("url", item.get("link", "")),
            source="Comfama",
        )

    def _parse_card(self, el, page_url: str) -> JobPosting | None:
        # Look for a meaningful link
        link_el = el.select_one("a[href*='vacante']") or el.select_one("a[href*='empleo']")
        if not link_el:
            return None

        title = self.clean_text(link_el.get_text())
        href = link_el.get("href", "")
        if not title or len(title) < 5:
            return None

        job_url = href if href.startswith("http") else f"https://www.comfama.com{href}"

        # Infer location from URL
        location = ""
        if "apartado" in page_url:
            location = "Apartadó, Antioquia"
        elif "turbo" in page_url:
            location = "Turbo, Antioquia"
        elif "carepa" in page_url:
            location = "Carepa, Antioquia"
        elif "chigorodo" in page_url:
            location = "Chigorodó, Antioquia"
        elif "uraba" in page_url:
            location = "Urabá, Antioquia"

        return JobPosting(
            title=title,
            company="Comfama",
            location=location,
            url=job_url,
            source="Comfama",
        )
