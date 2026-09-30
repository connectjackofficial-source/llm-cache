"""Tests for llm-cache."""
import tempfile
from pathlib import Path

from llm_cache.cache import LLMCache, make_key


def test_miss_then_hit():
    with tempfile.TemporaryDirectory() as d:
        c = LLMCache(Path(d) / "t.db")
        assert c.get("m", "p") is None
        c.set("m", "p", "ans")
        assert c.get("m", "p") == "ans"
        c.conn.close()
    print("test_miss_then_hit: ok")


def test_key_differs_by_model():
    k1 = make_key("gpt", "p")
    k2 = make_key("claude", "p")
    assert k1 != k2
    print("test_key_differs_by_model: ok")


def test_stats():
    with tempfile.TemporaryDirectory() as d:
        c = LLMCache(Path(d) / "t.db")
        c.set("m", "a", "1")
        c.set("m", "b", "2")
        assert c.stats()["entries"] == 2
        c.conn.close()
    print("test_stats: ok")


if __name__ == "__main__":
    test_miss_then_hit()
    test_key_differs_by_model()
    test_stats()
    print("llm-cache tests passed")
