# Urabá Job Market Scraper & Dashboard

Scrapes job postings from 6+ Colombian job portals for the Urabá region of Antioquia, processes the data (salary parsing, zone categorization, relevance scoring), and generates an interactive HTML dashboard.

## Quick Start

```bash
cd uraba_jobs
pip install -r requirements.txt
python main.py
```

This runs all scrapers, cleans the data, and outputs `dashboard.html` + `jobs.json`.

## Requirements

- Python 3.9+
- Dependencies: `pip install -r requirements.txt`
  - requests, beautifulsoup4, lxml, pandas, plotly

## How It Works

### 1. Scraping (`python main.py`)

Runs 6 scrapers in sequence with polite delays and retry logic:

| Source | Site | Method |
|---|---|---|
| Computrabajo | co.computrabajo.com | HTML parsing |
| elempleo.com | elempleo.com | HTML parsing |
| Magneto365 | magneto365.com | JSON-LD + HTML |
| Jooble | co.jooble.org | JSON-LD + HTML |
| Comfama | comfama.com | JSON-LD + HTML |
| Indeed | co.indeed.com | HTML (may require JS) |

Each scraper searches for jobs in Apartadó, Turbo, Carepa, Chigorodó, and other Urabá municipalities. Sites that block requests are handled gracefully — the pipeline continues with whatever data it collects.

### 2. Data Processing

Every scraped job goes through:

- **Salary parsing** — extracts min/max COP values from free-text strings like "$1.800.000 + comisiones"
- **Zone categorization** — maps locations to one of 12 Urabá municipalities (Apartadó, Turbo, Carepa, Chigorodó, Necoclí, Arboletes, etc.)
- **Contract detection** — classifies as `permanente`, `temporal`, or `sin especificar` based on keywords (indefinido, obra o labor, prestación de servicios, etc.)
- **Benefits extraction** — identifies mentioned benefits (salud, pensión, transporte, teletrabajo, comisiones, etc.)
- **Relevance scoring** — 0–1 score indicating how specifically the job relates to Urabá vs. generic Colombia postings
- **Deduplication** — removes duplicate postings across sources

### 3. Output Files

| File | Description |
|---|---|
| `dashboard.html` | Self-contained interactive dashboard (open in any browser) |
| `jobs.json` | Raw structured data for further analysis in pandas, notebooks, etc. |

## Dashboard Features

- 6 summary stat cards (total jobs, municipalities, companies, permanent, temporal, avg salary)
- 6 Plotly charts: jobs by zone, contract types, salary distribution, sources, relevance histogram, top companies
- Filterable by zone, contract type, source, relevance threshold, and free-text search
- Sortable table with direct links to each posting

## Alternative: Seed Data (`python seed_data.py`)

If direct HTTP scraping is blocked (corporate proxy, VPN, sandbox), run `seed_data.py` instead. It contains 64 real job postings collected from web search results (Feb 2026) and generates the same dashboard.

## Customization

### Add a new municipality

Edit `config.py` → `URABA_MUNICIPALITIES`:

```python
"New Municipality": ["keyword1", "keyword2"],
```

### Add a new job portal

1. Create `scrapers/new_portal_scraper.py` inheriting from `BaseScraper`
2. Implement `get_urls()` and `parse_listings()`
3. Register it in `scrapers/__init__.py`
4. Add it to the scraper list in `main.py`

### Adjust scraping behavior

In `config.py`:

- `REQUEST_TIMEOUT` — seconds before giving up on a page (default: 15)
- `RETRY_ATTEMPTS` — retries per URL (default: 2)
- `POLITE_DELAY` — seconds between requests (default: 1.5)

## Loading `jobs.json` in Python

```python
import pandas as pd
df = pd.read_json("jobs.json")

# Filter high-relevance jobs in Apartadó
apt = df[(df.zone == "Apartadó") & (df.relevance_score >= 0.8)]

# Salary stats
df.dropna(subset=["salary_max"]).groupby("zone")["salary_max"].describe()
```

## Project Structure

```
uraba_jobs/
├── main.py                 # Entry point — runs all scrapers + generates dashboard
├── seed_data.py            # Alternative — loads pre-collected data
├── config.py               # URLs, keywords, thresholds
├── data_schema.py          # JobPosting dataclass
├── requirements.txt
├── scrapers/
│   ├── base_scraper.py     # Abstract base with retry logic
│   ├── computrabajo_scraper.py
│   ├── elempleo_scraper.py
│   ├── indeed_scraper.py
│   ├── magneto365_scraper.py
│   ├── comfama_scraper.py
│   └── jooble_scraper.py
├── processing/
│   ├── cleaner.py          # Salary parsing, contract detection, benefits
│   ├── categorizer.py      # Zone/municipality mapping
│   └── relevance.py        # Urabá relevance scoring
└── dashboard/
    └── generator.py        # Builds self-contained HTML with Plotly
```
