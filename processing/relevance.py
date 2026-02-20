"""Score how relevant each job posting is to the Urabá region."""

import logging
from data_schema import JobPosting
import config

logger = logging.getLogger(__name__)


class RelevanceScorer:
    """Heuristic relevance scoring (0.0 – 1.0)."""

    @classmethod
    def score(cls, job: JobPosting) -> float:
        text = (
            job.title + " " + job.location + " " + job.company + " " + job.description
        ).lower()

        score = 0.0

        # Strong Urabá indicators → 0.8 – 1.0
        strong_hits = sum(1 for kw in config.STRONG_RELEVANCE_KEYWORDS if kw in text)
        if strong_hits >= 2:
            score = 1.0
        elif strong_hits == 1:
            score = 0.85

        # Zone already mapped to a Urabá municipality
        if job.zone and job.zone not in ("Sin especificar", "Antioquia (Other)"):
            score = max(score, 0.9)

        # Medium indicators
        if score < 0.5:
            medium_hits = sum(1 for kw in config.MEDIUM_RELEVANCE_KEYWORDS if kw in text)
            if medium_hits:
                score = max(score, 0.5)

        # Negative indicators (other cities) → penalize
        neg_hits = sum(1 for kw in config.NEGATIVE_RELEVANCE_KEYWORDS if kw in text)
        if neg_hits and score < 0.8:
            score = max(0.1, score - 0.3 * neg_hits)

        # Floor
        if score == 0.0:
            score = 0.3  # At least partial relevance since we searched regionally

        job.relevance_score = round(score, 2)
        return job.relevance_score
