"""Map raw location strings to Urabá municipalities."""

import logging
from data_schema import JobPosting
import config

logger = logging.getLogger(__name__)


class ZoneCategorizer:
    """Assign each job to a normalized municipality/zone."""

    @classmethod
    def categorize(cls, job: JobPosting) -> JobPosting:
        text = (job.location + " " + job.title + " " + job.description).lower()

        for municipality, keywords in config.URABA_MUNICIPALITIES.items():
            if any(kw in text for kw in keywords):
                job.zone = municipality
                return job

        # Generic Urabá mention
        if "urabá" in text or "uraba" in text:
            job.zone = "Urabá (General)"
        elif "antioquia" in text:
            job.zone = "Antioquia (Other)"
        else:
            job.zone = "Sin especificar"

        return job
