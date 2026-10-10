"""Tests for hit/miss counters."""
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from llm_cache.cache import LLMCache


def test_hit_miss_counters():
    with tempfile.TemporaryDirectory() as d:
        cache = LLMCache(Path(d) / "c.db")
        # miss then set then hit
        assert cache.get("m", "p") is None
        cache.set("m", "p", "r")
        assert cache.get("m", "p") == "r"
        assert cache.get("m", "p") == "r"
        stats = cache.stats()
        assert stats["hits"] == 2
        assert stats["misses"] == 1
        assert stats["hit_rate"] == round(2 / 3, 3)
        cache.close()
    print("test_hit_miss_counters: ok")


def test_ttl_miss_counts():
    with tempfile.TemporaryDirectory() as d:
        cache = LLMCache(Path(d) / "c.db", ttl_seconds=999999999)
        try:
            cache.set("m", "p", "r")
            # simulate expiry by setting ts to the past
            cache.conn.execute("UPDATE cache SET ts = 1")
            cache.conn.commit()
            assert cache.get("m", "p") is None  # expired -> miss
            stats = cache.stats()
            assert stats["misses"] == 1
            assert stats["hits"] == 0
        finally:
            cache.close()
    print("test_ttl_miss_counts: ok")


if __name__ == "__main__":
    test_hit_miss_counters()
    test_ttl_miss_counts()
    print("llm-cache counters tests passed")
