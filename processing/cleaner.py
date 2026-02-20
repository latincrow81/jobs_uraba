"""Data cleaning pipeline: salary parsing, contract detection, benefits extraction."""

import re
import logging
from typing import List, Tuple, Optional

from data_schema import JobPosting
from .categorizer import ZoneCategorizer
from .relevance import RelevanceScorer
import config

logger = logging.getLogger(__name__)


class DataCleaner:
    """Full cleaning + enrichment pipeline."""

    # ── Salary Parsing ────────────────────────────────────────────
    @staticmethod
    def parse_salary(raw: str) -> Tuple[Optional[float], Optional[float]]:
        """Extract (min, max) salary in COP from free-text salary strings."""
        if not raw:
            return None, None

        text = raw.lower().replace(".", "").replace(",", ".")

        # Pattern: "$1.500.000" or "1500000" or "1.5M"
        # Colombian salaries: dots as thousands separator
        numbers = re.findall(r'(\d[\d.]*)', text)
        if not numbers:
            return None, None

        parsed: List[float] = []
        for num_str in numbers:
            try:
                val = float(num_str.replace(".", ""))
                # If value is suspiciously small, multiply
                if val < 100:
                    val *= 1_000_000  # e.g. "1.5" → 1,500,000
                elif val < 10_000:
                    val *= 1_000      # e.g. "1500" → 1,500,000
                parsed.append(val)
            except ValueError:
                continue

        if not parsed:
            return None, None

        # Filter out unreasonable values (< min wage ~1.3M or > 50M)
        reasonable = [v for v in parsed if 1_000_000 <= v <= 50_000_000]
        if not reasonable:
            # Try raw values without filtering
            reasonable = sorted(parsed)

        if len(reasonable) >= 2:
            return min(reasonable), max(reasonable)
        elif len(reasonable) == 1:
            return reasonable[0], reasonable[0]
        return None, None

    # ── Contract Type Detection ───────────────────────────────────
    @staticmethod
    def detect_contract_type(job: JobPosting) -> JobPosting:
        text = (job.title + " " + job.description + " " + job.salary_raw).lower()

        if any(kw in text for kw in config.TEMPORAL_KEYWORDS):
            job.contract_type = "temporal"
            job.is_temporal = True
        elif any(kw in text for kw in config.PERMANENT_KEYWORDS):
            job.contract_type = "permanente"
            job.is_temporal = False
        else:
            job.contract_type = "sin especificar"
            job.is_temporal = False

        return job

    # ── Benefits Extraction ───────────────────────────────────────
    @staticmethod
    def extract_benefits(job: JobPosting) -> JobPosting:
        text = (job.description + " " + job.salary_raw).lower()
        found = []
        for benefit_name, keywords in config.BENEFITS_MAP.items():
            if any(kw in text for kw in keywords):
                found.append(benefit_name)
        job.benefits = found
        return job

    # ── Deduplication ─────────────────────────────────────────────
    @staticmethod
    def deduplicate(jobs: List[JobPosting]) -> List[JobPosting]:
        """Remove duplicate postings based on (title, company, location) tuple."""
        seen = set()
        unique = []
        for job in jobs:
            key = (
                job.title.lower().strip(),
                job.company.lower().strip(),
                job.location.lower().strip(),
            )
            if key not in seen:
                seen.add(key)
                unique.append(job)
        logger.info("Deduplication: %d → %d jobs", len(jobs), len(unique))
        return unique

    # ── Full Pipeline ─────────────────────────────────────────────
    @classmethod
    def clean_all(cls, jobs: List[JobPosting]) -> List[JobPosting]:
        """Run the entire cleaning + enrichment pipeline."""
        logger.info("Starting data cleaning pipeline on %d jobs", len(jobs))

        cleaned = []
        for job in jobs:
            # Parse salary
            job.salary_min, job.salary_max = cls.parse_salary(job.salary_raw)

            # Categorize zone
            ZoneCategorizer.categorize(job)

            # Detect contract type
            cls.detect_contract_type(job)

            # Extract benefits
            cls.extract_benefits(job)

            # Score relevance
            RelevanceScorer.score(job)

            cleaned.append(job)

        # Deduplicate
        cleaned = cls.deduplicate(cleaned)

        logger.info("Cleaning complete: %d jobs", len(cleaned))
        return cleaned
