"""Unified data schema for job postings across all sources."""

from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Optional, List


@dataclass
class JobPosting:
    title: str
    company: str
    location: str                          # Raw location text
    zone: str = ""                         # Normalized municipality
    salary_raw: str = ""                   # Original salary text
    salary_min: Optional[float] = None     # Extracted min (COP)
    salary_max: Optional[float] = None     # Extracted max (COP)
    salary_currency: str = "COP"
    contract_type: str = "unknown"         # temporal | permanent | unknown
    is_temporal: bool = False
    benefits: List[str] = field(default_factory=list)
    description: str = ""
    url: str = ""
    source: str = ""                       # Portal name
    date_posted: Optional[str] = None      # ISO format string
    relevance_score: float = 0.0           # 0-1
    scraped_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> 'JobPosting':
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})
