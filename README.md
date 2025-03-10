# Job Scraper

A Python script that scrapes job listings from multiple job posting platforms (Lever, Greenhouse, and Workday) using Google search.

## Features

- Searches for jobs across multiple platforms:
  - Lever.co
  - Greenhouse.io
  - Workday
- Implements caching to avoid duplicate job listings
- Detailed logging system
- Configurable job search parameters via JSON config
- Rate limiting protection with built-in delays
- Detailed logs are saved in the `logs` directory.

## Prerequisites

- Python 3.x
- Required Python packages:
  - google-search (for performing Google searches)
  - pickle (for caching)

## Usage

1. Install the required packages specified in the `requirements.txt` file.
```bash
pip install -r requirements.txt
```

2. Modify the `config.json` file to configure the job search parameters.

3. Run the script:
```bash
python job_scraper.py
```

Happy job hunting!
