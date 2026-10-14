"""Tests for llm-cache keys_matching."""
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from llm_cache.cache import LLMCache


def _cache():
    tmp = tempfile.TemporaryDirectory()
    c = LLMCache(Path(tmp.name) / "c.db")
    return c, tmp


def test_substring_match():
    c, tmp = _cache()
    c.set("gpt", "summarize the v2 changelog", "out1")
    c.set("claude", "deploy to production", "out2")
    c.set("gpt", "what changed in v2?", "out3")
    hits = c.keys_matching("v2")
    assert len(hits) == 2          # only the two prompts containing "v2"
    assert all(k["model"] == "gpt" for k in hits)
    assert all(k["key"] and k["ts"] for k in hits)
    c.close()
    tmp.cleanup()
    print("test_substring_match: ok")


def test_no_match():
    c, tmp = _cache()
    c.set("gpt", "hello world", "hi")
    assert c.keys_matching("zzz") == []
    c.close()
    tmp.cleanup()
    print("test_no_match: ok")


def test_limit():
    c, tmp = _cache()
    for i in range(5):
        c.set("gpt", f"common prefix {i}", f"r{i}")
    hits = c.keys_matching("common", limit=3)
    assert len(hits) == 3
    c.close()
    tmp.cleanup()
    print("test_limit: ok")


if __name__ == "__main__":
    test_substring_match()
    test_no_match()
    test_limit()
    print("llm-cache keys_matching tests passed")
