#!/usr/bin/env python3
"""
Urabá Job Market Scraper
========================
Scrapes job postings from 6 Colombian portals for the Urabá region of Antioquia,
processes the data, and generates an interactive HTML dashboard.

Usage:
    python main.py
"""

import json
import logging
import sys
from datetime import datetime
from pathlib import Path

# Ensure project root is on path
PROJECT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_DIR))

from scrapers import (
    ComputrabajoScraper,
    ElempleoScraper,
    IndeedScraper,
    Magneto365Scraper,
    ComfamaScraper,
    JoobleScraper,
)
from processing import DataCleaner
from dashboard import DashboardGenerator

# ── Logging ───────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(name)-18s  %(levelname)-7s  %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("main")

OUTPUT_DIR = PROJECT_DIR


def main():
    start = datetime.now()
    logger.info("=" * 60)
    logger.info("  Urabá Job Market Scraper  —  %s", start.strftime("%Y-%m-%d %H:%M"))
    logger.info("=" * 60)

    # ── 1. Scrape ─────────────────────────────────────────────────
    scrapers = [
        ComputrabajoScraper(),
        ElempleoScraper(),
        Magneto365Scraper(),
        JoobleScraper(),
        ComfamaScraper(),
        IndeedScraper(),
    ]

    all_jobs = []
    results_summary = []

    for scraper in scrapers:
        logger.info("─── %s ───", scraper.name)
        try:
            jobs = scraper.run()
            all_jobs.extend(jobs)
            results_summary.append((scraper.name, len(jobs), "OK"))
        except Exception as exc:
            logger.error("%s FAILED: %s", scraper.name, exc)
            results_summary.append((scraper.name, 0, f"FAILED: {exc}"))

    logger.info("Raw jobs collected: %d", len(all_jobs))

    if not all_jobs:
        logger.warning("No jobs were scraped from any source. The dashboard will be empty.")

    # ── 2. Clean & Process ────────────────────────────────────────
    logger.info("Cleaning and processing data...")
    cleaned = DataCleaner.clean_all(all_jobs)

    # ── 3. Save JSON ──────────────────────────────────────────────
    json_path = OUTPUT_DIR / "jobs.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(
            [j.to_dict() for j in cleaned],
            f,
            ensure_ascii=False,
            indent=2,
            default=str,
        )
    logger.info("Data saved → %s (%d jobs)", json_path, len(cleaned))

    # ── 4. Generate Dashboard ─────────────────────────────────────
    dashboard_path = OUTPUT_DIR / "dashboard.html"
    gen = DashboardGenerator(cleaned)
    gen.generate(str(dashboard_path))
    logger.info("Dashboard saved → %s", dashboard_path)

    # ── 5. Summary ────────────────────────────────────────────────
    elapsed = (datetime.now() - start).total_seconds()
    print("\n" + "=" * 60)
    print("  SCRAPING COMPLETE")
    print("=" * 60)
    print(f"\n  Time elapsed:  {elapsed:.1f}s")
    print(f"  Total jobs:    {len(cleaned)}")
    print()
    print("  Source Results:")
    for name, count, status in results_summary:
        print(f"    {name:20s}  {count:4d} jobs  [{status}]")
    print()

    # Zone breakdown
    from collections import Counter
    zone_counts = Counter(j.zone for j in cleaned)
    if zone_counts:
        print("  Jobs by Zone:")
        for zone, cnt in zone_counts.most_common(10):
            print(f"    {zone:25s}  {cnt:4d}")
        print()

    # Contract breakdown
    contract_counts = Counter(j.contract_type for j in cleaned)
    if contract_counts:
        print("  Jobs by Contract Type:")
        for ctype, cnt in contract_counts.most_common():
            print(f"    {ctype:25s}  {cnt:4d}")
        print()

    print(f"  Output files:")
    print(f"    Data:      {json_path}")
    print(f"    Dashboard: {dashboard_path}")
    print("=" * 60)


if __name__ == "__main__":
    main()
