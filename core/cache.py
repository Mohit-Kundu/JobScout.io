"""SQLite-backed deduplication cache for job listings."""

import os
import sqlite3


class JobCache:
    """Persistent cache of seen jobs in SQLite. Prunes entries older than 7 days at startup."""

    def __init__(self, db_path: str = "cache/jobs.db"):
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self._conn = sqlite3.connect(db_path)
        self._init_db()
        self._prune_old()

    def _init_db(self) -> None:
        self._conn.execute(
            """
            CREATE TABLE IF NOT EXISTS seen_jobs (
                url          TEXT PRIMARY KEY,
                title        TEXT,
                company      TEXT,
                first_seen   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        self._conn.commit()

    def _prune_old(self) -> None:
        """Remove entries older than 7 days."""
        self._conn.execute(
            "DELETE FROM seen_jobs WHERE first_seen < datetime('now', '-7 days')"
        )
        self._conn.commit()

    def is_duplicate(self, url: str, title: str = "", company: str = "") -> bool:
        """Return True if this URL was seen before; otherwise insert and return False."""
        url = (url or "").strip()
        if not url:
            return True
        try:
            self._conn.execute(
                "INSERT INTO seen_jobs (url, title, company) VALUES (?, ?, ?)",
                (url, title or None, company or None),
            )
            self._conn.commit()
            return False
        except sqlite3.IntegrityError:
            return True

    def close(self) -> None:
        self._conn.close()
