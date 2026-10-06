"""Test delete/clear."""
import tempfile
from pathlib import Path

from llm_cache.cache import LLMCache


def test_delete():
    with tempfile.TemporaryDirectory() as d:
        c = LLMCache(Path(d) / "t.db")
        c.set("m", "p", "ans")
        assert c.get("m", "p") == "ans"
        assert c.delete("m", "p") is True
        assert c.get("m", "p") is None
        assert c.delete("m", "p") is False
        c.conn.close()
    print("test_delete: ok")


def test_clear():
    with tempfile.TemporaryDirectory() as d:
        c = LLMCache(Path(d) / "t.db")
        c.set("m", "a", "1")
        c.set("m", "b", "2")
        assert c.clear() == 2
        assert c.stats()["entries"] == 0
        c.conn.close()
    print("test_clear: ok")


if __name__ == "__main__":
    test_delete()
    test_clear()
    print("delete/clear tests passed")
