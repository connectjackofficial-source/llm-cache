"""Tests for LRU eviction."""
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from llm_cache.cache import LLMCache


def test_eviction_drops_oldest():
    with tempfile.TemporaryDirectory() as d:
        cache = LLMCache(Path(d) / "c.db", max_entries=3)
        for i in range(5):
            cache.set(f"m{i}", f"p{i}", f"r{i}")
        assert cache.stats()["entries"] == 3
        # newest 3 are p2, p3, p4
        assert cache.get("m0", "p0") is None
        assert cache.get("m4", "p4") == "r4"
    print("test_eviction_drops_oldest: ok")


def test_lru_touch_keeps_recent():
    with tempfile.TemporaryDirectory() as d:
        cache = LLMCache(Path(d) / "c.db", max_entries=2)
        cache.set("m0", "p0", "r0")
        cache.set("m1", "p1", "r1")
        # touch m0 so it becomes the most recent
        assert cache.get("m0", "p0") == "r0"
        # adding a third entry evicts m1 (least recently used)
        cache.set("m2", "p2", "r2")
        assert cache.get("m1", "p1") is None
        assert cache.get("m0", "p0") == "r0"
    print("test_lru_touch_keeps_recent: ok")


if __name__ == "__main__":
    test_eviction_drops_oldest()
    test_lru_touch_keeps_recent()
    print("llm-cache eviction tests passed")
