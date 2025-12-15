# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2025-12-13


### Added

- Initial release
- `WordnetEditor` class for editing WordNet lexicons
- Helper functions for creating wn.lmf-compatible dict structures:
  - `make_lexical_resource()`
  - `make_lexicon()`
  - `make_lexical_entry()`
  - `make_lemma()`
  - `make_sense()`
  - `make_synset()`
  - `make_definition()`
  - `make_example()`
  - `make_relation()`
  - `make_form()`
- Support for creating new lexicons from scratch
- Support for loading existing lexicons from the wn database
- Synset operations: create, modify, remove, add relations
- Entry operations: create, find, remove, add to synsets
- Export using `wn.lmf.dump()`
- Commit to database using `wn.add_lexical_resource()`
