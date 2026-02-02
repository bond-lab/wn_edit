# CLAUDE.md

## Project overview

wn_edit is a Python editing extension for the [wn](https://github.com/goodmami/wn) WordNet library. It works directly with `wn.lmf` TypedDict structures internally, using `wn.lmf.dump()` for export and `wn.add_lexical_resource()` for database commits. Relation constants come from `wn.constants`.

Requires Python 3.10+ and wn >= 1.0.0.

## Development environment

Always use the hatch environment for running commands (tests, pip installs, benchmarks, etc.) — never use the system Python directly. All commands below use `hatch run`.

## Commands

- `hatch run test` — fast tests only (default, skips `@pytest.mark.slow`)
- `hatch run test-slow` — slow round-trip tests only (downloads OEWN, can take 15+ minutes)
- `hatch run test-all` — all tests
- `hatch run test-cov` — fast tests with coverage

## Testing

- Slow tests can take up to 30 minutes; use extended timeouts when running them
- All tests use a local `.wn_data/` directory (via `tests/conftest.py`), not the global `~/.wn_data`
- The `.wn_data/` directory is gitignored and caches downloaded wordnets; do not delete it between runs unless you want a fresh download
- Slow tests download OEWN (~1.3M entries) on first run; subsequent runs reuse the cache

## Architecture notes

- `WordnetEditor._load_from_database()` tries two paths:
  1. `_load_from_database_bulk` — ~20 bulk SQL queries (fastest, ~10s for OEWN)
  2. `_load_from_database_xml` — XML roundtrip via `wn.export()` + `wn.lmf.load()` (~140s, public API fallback)
  The bulk path falls back on `ImportError`, `AttributeError`, or `sqlite3.OperationalError`.
- The bulk path queries `wn._db.connect()` directly and matches the exporter's output exactly. It relies on wn's internal schema, so it falls back gracefully if the schema changes.
- The wn database does **not** preserve the original LMF version. When loading from DB, `DEFAULT_LMF_VERSION` (1.4) is used. Users can override with `lmf_version=` in the constructor.
- `wn.export()` with `version='1.0'` drops `lexfile` and `count` data. Versions 1.1+ preserve them.
- In wn >= 1.0, `synset.ili` returns a `str` directly, not an object with an `.id` attribute.

## Code style

- Follow existing patterns in the codebase
- Use `wn.constants` for relation types and parts of speech, not hardcoded sets
- Helper functions (`make_synset`, `make_lexical_entry`, etc.) must include `'meta': None` for `wn.add_lexical_resource()` compatibility
