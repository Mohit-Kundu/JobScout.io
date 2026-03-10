# JobScout.io

A Python application that scrapes job listings from multiple job posting platforms (Lever, Greenhouse, and Workday) using DuckDuckGo search.

## Features

- Searches for jobs across multiple platforms:
  - Lever.co
  - Greenhouse.io
  - Workday
- SQLite cache of seen jobs (pruned to last 7 days at startup)
- CSV output (`jobs.csv`: title, company, ats, url, posted_at, scraped_at)
- Detailed logging in the `logs/` directory
- Configurable via `config/config.yaml`
- Rate limiting protection with built-in delays

## Prerequisites

- Python 3.x
- Required Python packages (see `requirements.txt`):
  - ddgs (DuckDuckGo search), schedule, pytz

## Usage

1. Install the required packages specified in the `requirements.txt` file.
```bash
pip install -r requirements.txt
```

2. Edit `config/config.yaml` to set job titles, region, and other options.

3. Run the scraper:
```bash
python main.py
```

4. Run tests (optional):
```bash
pytest test/
```

Happy job hunting!
