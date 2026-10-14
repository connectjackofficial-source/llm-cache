"""Tests for llm-cache maintenance: evict_older_than and top_entries."""
import sys
import tempfile
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from llm_cache.cache import LLMCache


def _cache():
    tmp = tempfile.TemporaryDirectory()
    c = LLMCache(Path(tmp.name) / "c.db")
    return c, tmp


def test_evict_older_than():
    c, tmp = _cache()
    c.set("gpt", "hello", "hi there")
    old = int(time.time()) - 1000
    c.conn.execute(
        "INSERT INTO cache (key, model, prompt, response, ts) VALUES (?,?,?,?,?)",
        ("old-key", "gpt", "old", "old resp", old))
    c.conn.commit()
    removed = c.evict_older_than(seconds=600)
    assert removed == 1  # only the old entry goes
    assert c.get("gpt", "hello") == "hi there"  # fresh entry survives
    c.close()
    tmp.cleanup()
    print("test_evict_older_than: ok")


def test_evict_nothing():
    c, tmp = _cache()
    c.set("gpt", "hello", "hi there")
    removed = c.evict_older_than(seconds=60 * 60 * 24 * 365)
    assert removed == 0
    c.close()
    tmp.cleanup()
    print("test_evict_nothing: ok")


def test_top_entries_newest_first():
    c, tmp = _cache()
    c.set("gpt", "first", "resp-one")
    c.set("claude", "second", "resp-two")
    # force distinct timestamps so ordering is deterministic
    c.conn.execute("UPDATE cache SET ts = ts + 1 WHERE prompt = 'second'")
    c.conn.commit()
    top = c.top_entries(n=5)
    assert len(top) == 2
    assert top[0]["model"] == "claude"  # newest first
    assert top[1]["prompt"] == "first"
    assert all("response" in t and "ts" in t for t in top)
    c.close()
    tmp.cleanup()
    print("test_top_entries_newest_first: ok")


def test_top_entries_empty():
    c, tmp = _cache()
    assert c.top_entries() == []
    c.close()
    tmp.cleanup()
    print("test_top_entries_empty: ok")


if __name__ == "__main__":
    test_evict_older_than()
    test_evict_nothing()
    test_top_entries_newest_first()
    test_top_entries_empty()
    print("llm-cache maintenance tests passed")
