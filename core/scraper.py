"""Search and scrape logic."""

import csv
import re
import time
from datetime import datetime
from pathlib import Path

from ddgs import DDGS

from core.cache import JobCache
from core.config import load_config
from core.logger import setup_logging


# Sites we restrict search to (config could extend this later)
JOB_SITES = "site:lever.co OR site:greenhouse.io OR site:myworkdayjobs.com"

CSV_HEADER = ("title", "company", "ats", "url", "posted_at", "scraped_at")


def infer_ats(url: str) -> str:
    """Infer ATS from job URL."""
    url_lower = (url or "").lower()
    if "greenhouse.io" in url_lower or "job-boards.greenhouse.io" in url_lower:
        return "greenhouse"
    if "lever.co" in url_lower or "jobs.lever.co" in url_lower:
        return "lever"
    if "myworkdayjobs.com" in url_lower or "wd1.myworkdayjobs.com" in url_lower:
        return "workday"
    return ""


def infer_company(title: str) -> str:
    """Try to extract company from result title (e.g. 'Job Application for X at Company')."""
    if not title:
        return ""
    # "Job Application for Data Scientist, Customer Analytics at Cresta" -> Cresta
    m = re.search(r"\s+at\s+([^|–\-]+?)(?:\s*[|–\-]|$)", title, re.IGNORECASE)
    if m:
        return m.group(1).strip()
    # "Data Scientist - Company Name" or "Company - Job Title"
    for sep in (" - ", " – ", " — "):
        if sep in title:
            parts = title.split(sep, 1)
            if len(parts) == 2:
                return parts[1].strip()
    return ""


def build_query(job_title: str) -> str:
    """Build search query for a job title restricted to known job boards."""
    return f'{JOB_SITES} "{job_title}"'


def format_listing(job_number: int, job_title: str, title: str, url: str, description: str) -> str:
    """Format a single job result for logging."""
    sep = "=" * 80
    return f"""
{sep}
Job {job_number}:
Search Query: {job_title}
Job Title: {title or "N/A"}
URL: {url or "N/A"}
Description: {description or "N/A"}
{sep}
"""


def _append_job_csv(csv_path: str | Path, title: str, company: str, ats: str, url: str, scraped_at: str) -> None:
    """Append one row to jobs.csv; write header if file is new."""
    path = Path(csv_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    file_exists = path.exists()
    with open(path, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(CSV_HEADER)
        writer.writerow([title, company, ats, url, "", scraped_at])


def scrape_jobs(
    config_path: str | Path | None = None,
    db_path: str = "cache/jobs.db",
    csv_path: str = "jobs.csv",
) -> None:
    """Run the full job search: load config, query DuckDuckGo, dedupe via SQLite, write new jobs to CSV."""
    logger = setup_logging()
    config = load_config(config_path)
    cache = JobCache(db_path=db_path)

    region = config.get("region", "us")
    job_titles = config.get("job_titles", [])
    delay_between_titles = 2

    logger.info("Starting job search...")
    total_new = 0
    total_duplicates = 0

    try:
        for job_title in job_titles:
            logger.info("Searching for: %s", job_title)
            query = build_query(job_title)

            try:
                ddgs = DDGS()
                results_list = ddgs.text(
                    query,
                    max_results=5,
                    region=f"{region}-en",
                )
                logger.info("Query: %s -> raw results from DuckDuckGo: %d", query, len(results_list))

                jobs_found = 0
                dupes = 0
                skipped_no_url = 0
                scraped_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                for result in results_list:
                    title = result.get("title", "") or ""
                    url = (result.get("href", "") or "").strip()
                    description = result.get("body", "") or ""

                    if not url:
                        skipped_no_url += 1
                        continue

                    company = infer_company(title)
                    if cache.is_duplicate(url, title, company):
                        dupes += 1
                        total_duplicates += 1
                        continue

                    jobs_found += 1
                    total_new += 1
                    ats = infer_ats(url)
                    _append_job_csv(csv_path, title, company, ats, url, scraped_at)
                    logger.info(format_listing(jobs_found, job_title, title, url, description))
                    time.sleep(1)

                logger.info(
                    "Found %d new jobs, %d duplicates, %d skipped (no URL) for %s",
                    jobs_found,
                    dupes,
                    skipped_no_url,
                    job_title,
                )
                time.sleep(delay_between_titles)

            except Exception as e:
                err_str = str(e)
                if "429" in err_str or "Too Many Requests" in err_str:
                    logger.warning(
                        "Rate-limited the request for '%s' (429). "
                        "Consider using a SERP API or scraping job boards directly.",
                        job_title,
                    )
                else:
                    logger.error("Error searching for %s: %s", job_title, err_str)

        logger.info("Search complete. Total new jobs found: %d", total_new)
        logger.info("Total duplicate jobs skipped: %d", total_duplicates)
    finally:
        cache.close()
