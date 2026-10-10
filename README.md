# llm-cache

> Cache LLM responses locally. Same model + same prompt = same answer, zero
> new API calls. Saves tokens, money, and latency on repeated calls.

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](#)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](#)

Every time you re-run a prompt against the same model, you pay again.
`llm-cache` is a 50-line SQLite cache: hash `model + prompt`, store the
response, serve it back on repeat.

## Usage

```python
from llm_cache.cache import LLMCache

cache = LLMCache()  # ~/.llm-cache/cache.db

hit = cache.get("gpt-4o", "explain caching")
if hit:
    answer = hit
else:
    answer = call_llm("gpt-4o", "explain caching")
    cache.set("gpt-4o", "explain caching", answer)
```

With a TTL (seconds):

```python
cache = LLMCache(ttl_seconds=3600)  # expire after 1 hour
```

With a size cap (LRU eviction):

```python
cache = LLMCache(max_entries=1000)  # drop the oldest entries when full
```

Hits refresh the recency timestamp, so frequently used entries survive
eviction.

## Stats

```python
print(cache.stats())
# {"entries": 42, "max_entries": null, "hits": 300, "misses": 150, "hit_rate": 0.667}
cache.delete("gpt-4o", "explain caching")  # drop one entry
cache.clear()  # drop all
```

Hits and misses are tracked persistently, so you can tell whether the cache
is actually saving you calls. Use it as a context manager to close the
SQLite connection automatically:

```python
with LLMCache() as cache:
    cache.get("gpt-4o", "explain caching")
```

## Batch API

For pipelines that replay many cached prompts, use the batch methods
(one commit instead of one per key):

```python
cache.set_many([
    ("gpt-4o", "q1", "a1"),
    ("sonnet", "q2", "a2"),
])
found = cache.get_many([("gpt-4o", "q1"), ("sonnet", "missing"), ("sonnet", "q2")])
# {0: "a1", 2: "a2"}  -- only hits, indexed by input position
```

`set_many()` still honors `max_entries` eviction.

## CLI

```bash
python -m llm_cache.cli stats
python -m llm_cache.cli clear
```

## License

MIT
