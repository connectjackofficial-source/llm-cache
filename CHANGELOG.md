# Changelog

## 0.5.0 - 2026-10-10

- `set_many()` / `get_many()` batch API for pipelines
- Batch writes honor `max_entries` eviction

## 0.4.0 - 2026-10-10

- Persistent hit/miss counters
- `hit_rate` in stats
- `close()` / context-manager support

## 0.3.0 - 2026-10-08

- LRU eviction via `max_entries`
- Hits refresh recency timestamp
- `stats()` reports max_entries

## 0.2.0 - 2026-10-06

- delete / clear methods
- CLI (stats, clear)

## 0.1.0 - 2026-09-29

- Initial release
- SQLite cache with TTL
- get/set/stats API
