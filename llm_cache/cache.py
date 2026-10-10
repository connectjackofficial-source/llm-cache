"""llm-cache: cache LLM responses locally to save tokens.

Key = hash(model + prompt). SQLite storage, optional TTL.
"""
from __future__ import annotations

import hashlib
import json
import os
import sqlite3
import time
from pathlib import Path
from typing import Optional


def db_path() -> Path:
    root = os.environ.get("LLM_CACHE_DIR")
    if root:
        return Path(root) / "cache.db"
    return Path.home() / ".llm-cache" / "cache.db"


SCHEMA = """
CREATE TABLE IF NOT EXISTS cache (
    key TEXT PRIMARY KEY,
    model TEXT,
    prompt TEXT,
    response TEXT,
    ts INTEGER
);
CREATE TABLE IF NOT EXISTS counters (
    name TEXT PRIMARY KEY,
    value INTEGER NOT NULL DEFAULT 0
);
"""


def make_key(model: str, prompt: str) -> str:
    return hashlib.sha256(f"{model}||{prompt}".encode()).hexdigest()[:32]


class LLMCache:
    def __init__(self, path: Optional[Path] = None, ttl_seconds: int = 0,
                 max_entries: int = 0):
        self.path = Path(path) if path else db_path()
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.ttl = ttl_seconds
        self.max_entries = max_entries
        self.conn = sqlite3.connect(self.path)
        self.conn.executescript(SCHEMA)

    def close(self):
        self.conn.close()

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()

    def _counter(self, name: str, delta: int = 1) -> int:
        self.conn.execute(
            "INSERT INTO counters (name, value) VALUES (?, ?) "
            "ON CONFLICT(name) DO UPDATE SET value = value + excluded.value",
            (name, delta))
        return self._counter_value(name)

    def _counter_value(self, name: str) -> int:
        row = self.conn.execute(
            "SELECT value FROM counters WHERE name = ?", (name,)).fetchone()
        return row[0] if row else 0

    def get(self, model: str, prompt: str) -> Optional[str]:
        key = make_key(model, prompt)
        row = self.conn.execute(
            "SELECT response, ts FROM cache WHERE key = ?", (key,)).fetchone()
        if not row:
            self._counter("misses")
            self.conn.commit()
            return None
        if self.ttl and (time.time() - row[1]) > self.ttl:
            self._counter("misses")
            self.conn.commit()
            return None
        self._counter("hits")
        # LRU touch: mark this entry as most recently used
        self.conn.execute("UPDATE cache SET ts = ? WHERE key = ?",
                          (int(time.time()), key))
        self.conn.commit()
        return row[0]

    def set(self, model: str, prompt: str, response: str) -> str:
        key = make_key(model, prompt)
        self.conn.execute(
            "INSERT OR REPLACE INTO cache (key, model, prompt, response, ts) "
            "VALUES (?,?,?,?,?)",
            (key, model, prompt, response, int(time.time())))
        if self.max_entries:
            self._evict()
        self.conn.commit()
        return key

    def _evict(self):
        """Drop the oldest entries until we are under max_entries."""
        while True:
            row = self.conn.execute(
                "SELECT COUNT(*) FROM cache").fetchone()
            if row[0] <= self.max_entries:
                break
            self.conn.execute(
                "DELETE FROM cache WHERE key = (SELECT key FROM cache "
                "ORDER BY ts ASC LIMIT 1)")

    def stats(self) -> dict:
        row = self.conn.execute("SELECT COUNT(*) FROM cache").fetchone()
        hits = self._counter_value("hits")
        misses = self._counter_value("misses")
        total = hits + misses
        return {
            "entries": row[0],
            "max_entries": self.max_entries or None,
            "hits": hits,
            "misses": misses,
            "hit_rate": round(hits / total, 3) if total else None,
        }

    def delete(self, model: str, prompt: str) -> bool:
        key = make_key(model, prompt)
        cur = self.conn.execute("DELETE FROM cache WHERE key = ?", (key,))
        self.conn.commit()
        return cur.rowcount > 0

    def clear(self) -> int:
        cur = self.conn.execute("DELETE FROM cache")
        self.conn.commit()
        return cur.rowcount
