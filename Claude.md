# CLAUDE.md

## Project overview

wn_edit is a Python editing extension for the [wn](https://github.com/goodmami/wn) WordNet library. It works directly with `wn.lmf` TypedDict structures internally, using `wn.lmf.dump()` for export and `wn.add_lexical_resource()` for database commits. Relation constants come from `wn.constants`.

Requires Python 3.10+ and wn >= 1.0.0.

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

- `WordnetEditor` loads from the wn database via a roundtrip: `wn.export()` to temp XML, then `wn.lmf.load()` back into a dict. This is in `_load_from_database()`.
- The wn database does **not** preserve the original LMF version. When loading from DB, `wn.export()`'s default version is used (currently 1.4). Users can override with `lmf_version=` in the constructor.
- `wn.export()` with `version='1.0'` drops `lexfile` and `count` data. Versions 1.1+ preserve them.
- In wn >= 1.0, `synset.ili` returns a `str` directly, not an object with an `.id` attribute.

## Code style

- Follow existing patterns in the codebase
- Use `wn.constants` for relation types and parts of speech, not hardcoded sets
- Helper functions (`make_synset`, `make_lexical_entry`, etc.) must include `'meta': None` for `wn.add_lexical_resource()` compatibility
