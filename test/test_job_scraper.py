"""Tests for core package."""

import tempfile
from pathlib import Path

import pytest

from core.cache import JobCache
from core.config import load_config
from core.scraper import build_query, format_listing, infer_ats, infer_company


def test_load_config():
    """Config loads from YAML and has expected keys."""
    config = load_config()
    assert "job_titles" in config
    assert "region" in config
    assert isinstance(config["job_titles"], list)


def test_build_query():
    """Query restricts to job sites and includes title."""
    q = build_query("software engineer")
    assert "lever.co" in q
    assert "greenhouse.io" in q
    assert "software engineer" in q


def test_format_listing():
    """Format produces a string with title and URL."""
    out = format_listing(
        1,
        "software engineer",
        "DevOps Engineer",
        "https://example.com/job",
        "Great role."
    )
    assert "DevOps Engineer" in out
    assert "https://example.com/job" in out


def test_infer_ats():
    """ATS is inferred from URL."""
    assert infer_ats("https://boards.greenhouse.io/company/jobs/123") == "greenhouse"
    assert infer_ats("https://jobs.lever.co/company/abc") == "lever"
    assert infer_ats("https://company.wd1.myworkdayjobs.com/External/job/123") == "workday"
    assert infer_ats("https://other.com/job") == ""


def test_infer_company():
    """Company is extracted from title when possible."""
    assert infer_company("Job Application for Data Scientist at Cresta") == "Cresta"
    assert infer_company("Data Scientist - Stripe") == "Stripe"
    assert infer_company("Plain Title") == ""


def test_cache_deduplication():
    """Cache marks duplicates by URL and allows new jobs."""
    with tempfile.TemporaryDirectory() as tmp:
        db_path = Path(tmp) / "jobs.db"
        cache = JobCache(db_path=str(db_path))

        assert cache.is_duplicate("https://a.com/job/1", "Title A", "Co A") is False
        assert cache.is_duplicate("https://a.com/job/1", "Title A", "Co A") is True
        assert cache.is_duplicate("https://b.com/job/2", "Title B", "Co B") is False

        cache.close()
