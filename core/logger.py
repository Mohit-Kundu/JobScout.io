"""Logging setup."""

import logging
from datetime import datetime
from pathlib import Path


def setup_logging(
    log_dir: str | Path = "logs",
    log_prefix: str = "demo_scraper",
) -> logging.Logger:
    """Configure file + console logging and return the package logger."""
    log_dir = Path(log_dir)
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / f"{log_prefix}_{datetime.now():%Y%m%d_%H%M%S}.log"

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(log_file, encoding="utf-8"),
            logging.StreamHandler(),
        ],
        force=True,
    )
    return logging.getLogger("core")
