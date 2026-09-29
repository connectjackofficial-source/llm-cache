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
"""


def make_key(model: str, prompt: str) -> str:
    return hashlib.sha256(f"{model}||{prompt}".encode()).hexdigest()[:32]


class LLMCache:
    def __init__(self, path: Optional[Path] = None, ttl_seconds: int = 0):
        self.path = Path(path) if path else db_path()
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.ttl = ttl_seconds
        self.conn = sqlite3.connect(self.path)
        self.conn.executescript(SCHEMA)

    def get(self, model: str, prompt: str) -> Optional[str]:
        key = make_key(model, prompt)
        row = self.conn.execute(
            "SELECT response, ts FROM cache WHERE key = ?", (key,)).fetchone()
        if not row:
            return None
        if self.ttl and (time.time() - row[1]) > self.ttl:
            return None
        return row[0]

    def set(self, model: str, prompt: str, response: str) -> str:
        key = make_key(model, prompt)
        self.conn.execute(
            "INSERT OR REPLACE INTO cache (key, model, prompt, response, ts) "
            "VALUES (?,?,?,?,?)",
            (key, model, prompt, response, int(time.time())))
        self.conn.commit()
        return key

    def stats(self) -> dict:
        row = self.conn.execute("SELECT COUNT(*) FROM cache").fetchone()
        return {"entries": row[0]}
