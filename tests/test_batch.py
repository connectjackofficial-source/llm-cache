"""Tests for batch get/set."""
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from llm_cache.cache import LLMCache


def test_set_many():
    with tempfile.TemporaryDirectory() as d:
        cache = LLMCache(Path(d) / "c.db")
        try:
            items = [
                ("gpt-4o", "q1", "a1"),
                ("sonnet", "q2", "a2"),
                ("gpt-4o", "q3", "a3"),
            ]
            n = cache.set_many(items)
            assert n == 3
            assert cache.stats()["entries"] == 3
            assert cache.get("gpt-4o", "q1") == "a1"
            assert cache.get("sonnet", "q2") == "a2"
        finally:
            cache.close()
    print("test_set_many: ok")


def test_get_many_hits_and_misses():
    with tempfile.TemporaryDirectory() as d:
        cache = LLMCache(Path(d) / "c.db")
        try:
            cache.set("gpt-4o", "q1", "a1")
            cache.set("sonnet", "q2", "a2")
            found = cache.get_many([("gpt-4o", "q1"),
                                    ("sonnet", "missing"),
                                    ("sonnet", "q2")])
            assert found == {0: "a1", 2: "a2"}
        finally:
            cache.close()
    print("test_get_many_hits_and_misses: ok")


def test_set_many_respects_max_entries():
    with tempfile.TemporaryDirectory() as d:
        cache = LLMCache(Path(d) / "c.db", max_entries=2)
        try:
            cache.set_many([("m", f"q{i}", f"a{i}") for i in range(5)])
            assert cache.stats()["entries"] == 2
        finally:
            cache.close()
    print("test_set_many_respects_max_entries: ok")


if __name__ == "__main__":
    test_set_many()
    test_get_many_hits_and_misses()
    test_set_many_respects_max_entries()
    print("llm-cache batch tests passed")
