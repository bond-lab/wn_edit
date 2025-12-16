# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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
