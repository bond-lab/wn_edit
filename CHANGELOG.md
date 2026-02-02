# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed

- **Performance**: `_load_from_database()` now uses bulk SQL queries (~20 total)
  instead of an XML roundtrip, reducing OEWN load time from ~140s to ~10s.
  Falls back to the XML roundtrip automatically if the wn schema changes.
- `_load_from_database()` now uses `wn.export()`'s default LMF version (currently
  1.4) instead of hardcoding 1.1. The wn database does not preserve the original
  LMF version of imported data; use the `lmf_version` parameter in `__init__` to
  override if a specific version is needed.
- Minimum `wn` dependency bumped from 0.9.0 to 1.0.0 (required for LMF 1.4
  export support).

### Fixed

- Round-trip fidelity tests now pass: removing the hardcoded LMF 1.1 version
  eliminates DOCTYPE mismatches between original and editor exports.
- ILI integration tests updated for `wn>=1.0` API where `synset.ili` returns
  a `str` directly instead of an object with an `.id` attribute.
- All tests now use a local `.wn_data/` directory (via shared `conftest.py`)
  instead of the global `~/.wn_data`, avoiding issues with corrupted or
  incompatible cached downloads.

## [0.3.2] - 2025-12-22

### Added

- `set_id()` method to change the lexicon ID
- Metadata override parameters when loading from database:
  - `lexicon_id`, `label`, `version`, `lmf_version` can now be passed to `WordnetEditor()`
    when loading an existing lexicon to create derivative works
  - Parameters default to `None`, preserving original values unless explicitly set
- Sense index (`_sense_by_id`) for O(1) sense lookups
- New tests:
  - `TestWordnetEditorMetadataOverride` - tests for metadata override via setter methods
  - `TestWordnetEditorInitOverride` - tests for metadata override via `__init__` parameters
  - `test_add_sense_relation_after_load_from_database` - regression test for ChainNet use case

### Changed

- **Performance**: `add_sense_relation()` now uses O(1) index lookup instead of O(n)
  linear search through all entries and senses
- `_rebuild_indexes()` now also builds the sense index
- `add_word_to_synset()` now maintains the sense index
- `remove_synset()` now properly maintains all indexes (entry, lemma, and sense)
- `remove_entry()` now properly maintains the sense index

### Fixed

- Round-trip fidelity: loading and re-exporting a wordnet now preserves the original
  `lmf_version` instead of always overwriting with 1.4
- Test normalization now handles trailing whitespace in text content that may be
  stripped by the wn.lmf load/dump cycle

### Removed

- Cleaned up obsolete comments referencing old key name alternatives

## [0.3.1] - 2025-12-16

### Added

- Validation for parts of speech using `wn.constants.PARTS_OF_SPEECH`:
  - `validate_pos()` function to check POS values
  - `make_lemma()` and `make_synset()` now validate POS automatically
- Validation for adjective positions using `ADJPOSITIONS`:
  - `validate_adjposition()` function to check adjposition values ('a', 'p', 'ip')
  - `make_sense()` now validates adjposition if provided
- Validation for sense counts:
  - `validate_count()` function to ensure counts are non-negative integers
  - `make_count()` helper function to create count dictionaries with validation
- New constants exported:
  - `PARTS_OF_SPEECH` - valid part of speech tags (from `wn.constants`)
  - `ADJPOSITIONS` - valid adjective positions ('a', 'p', 'ip')

## [0.3.0] - 2025-12-16

### Added

- Integration test suite (`test_wn_integration.py`) verifying `commit()` works correctly:
  - Tests for querying committed synsets via `wn.synsets()`
  - Tests for lemmas, hypernyms, hypernym paths, examples
  - Tests for ILI identifier support
  - Tests for `wn.Wordnet()`, `wn.words()`, `wn.senses()`
  - Full round-trip test: create → commit → query → export
- Round-trip fidelity test suite (`test_roundtrip_fidelity.py`):
  - Tests that loading OEWN, making minimal changes, and exporting preserves all data
  - Marked as `slow` and skipped by default (run with `hatch test -- -m slow`)
  - Automatic OEWN download if not installed

### Fixed

- `commit()` now works correctly with `wn.add_lexical_resource()`:
  - All data structures now include required `meta` key (even if `None`)
  - Affected: `make_lexicon()`, `make_synset()`, `make_sense()`, `make_lexical_entry()`,
    `make_definition()`, `make_example()`, `make_relation()`
- `remove_synset()` now properly cleans up orphaned lexical entries:
  - Entries with no remaining senses are automatically removed
  - Entries with other senses are preserved

### Changed

- Test cleanup now uses `wn.remove()` with wildcard patterns for reliable isolation

## [0.2.0] - 2025-12-15

### Added

- Full compatibility with `wn.lmf` TypedDict structures
- Key names updated to match wn.lmf expectations:
  - `entries` (not `lexical_entries`)
  - `writtenForm` (not `written_form`)
  - `partOfSpeech` (not `part_of_speech`)
  - `relType` (not `rel_type`)

## [0.1.0] - 2024-12-15

### Added

- `WordnetEditor` class for creating and modifying WordNet lexicons
- Support for creating new lexicons from scratch
- Support for loading existing lexicons from the wn database
- `WordnetEditor.load_from_file()` class method for loading from WN-LMF XML
- Synset operations:
  - `create_synset()` - Create synsets with definitions, words, and examples
  - `modify_synset()` - Update synset definitions and examples
  - `remove_synset()` - Remove synsets from the lexicon
  - `add_synset_relation()` - Add relations between synsets
  - `get_synset()` - Retrieve synset by ID
- Entry/word operations:
  - `create_entry()` - Create lexical entries
  - `add_word_to_synset()` - Add words to existing synsets
  - `find_entries()` - Search entries by lemma
  - `remove_entry()` - Remove entries from the lexicon
- Sense operations:
  - `add_sense_relation()` - Add relations between senses
- Metadata operations:
  - `get_metadata()` - Get lexicon metadata
  - `set_version()`, `set_label()`, `set_email()`, etc. - Update individual fields
  - `update_metadata()` - Update multiple metadata fields at once
- Export and commit:
  - `export()` - Export to WN-LMF XML using `wn.lmf.dump()`
  - `commit()` - Commit to wn database using `wn.add_lexical_resource()`
  - Optional `validate_first` parameter for both methods
- Validation:
  - `validate()` - Validate lexicon using `wn.validate`
  - Relation type validation using `wn.constants.SYNSET_RELATIONS` and `SENSE_RELATIONS`
- Helper functions for creating wn.lmf-compatible data structures:
  - `make_lexical_resource()`, `make_lexicon()`, `make_synset()`
  - `make_lexical_entry()`, `make_lemma()`, `make_sense()`
  - `make_definition()`, `make_example()`, `make_relation()`, `make_form()`
- `stats()` method for lexicon statistics
- Comprehensive test suite with 37 tests
- Full documentation in README.md and CONTRIBUTING.md

### Design Decisions

- Uses `wn.lmf` TypedDict structures directly for full compatibility
- Key names match wn.lmf expectations (`entries`, `writtenForm`, `partOfSpeech`, `relType`)
- Relation constants imported from `wn.constants` (not hardcoded)
- Default LMF version: 1.4
