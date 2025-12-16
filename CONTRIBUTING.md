# Contributing to wn_edit

Thank you for your interest in contributing to wn_edit! This document provides guidelines and instructions for development.

## Development Setup

### Prerequisites

- Python 3.10 or higher
- [Hatch](https://hatch.pypa.io/) for project management

### Getting Started

1. Clone the repository:

   ```bash
   git clone https://github.com/yourusername/wn_edit.git
   cd wn_edit
   ```

2. Install Hatch (if not already installed):

   ```bash
   pip install hatch
   ```

3. Create and activate the development environment:

   ```bash
   hatch shell
   ```

   This will create a virtual environment with all dependencies installed, including the `wn` package.

## Running Tests

Run the test suite with:

```bash
hatch test
```

For verbose output:

```bash
hatch test -v
```

To run specific tests:

```bash
hatch test tests/test_editor.py::TestWordnetEditorSynsets
hatch test tests/test_editor.py::TestWordnetEditorSynsets::test_create_synset_basic
```

With coverage:

```bash
hatch test --cover
```

## Code Quality

### Type Checking

Run mypy for type checking:

```bash
hatch run mypy:check
```

### Linting

The project uses Ruff for linting:

```bash
hatch fmt --check   # Check only
hatch fmt           # Auto-fix
```

## Project Structure

```
wn_edit/
├── wn_edit/                # Source package
│   ├── __init__.py         # Public API exports
│   ├── editor.py           # Main WordnetEditor class and helpers
│   └── version.py          # Version string
├── tests/
│   ├── __init__.py
│   └── test_editor.py      # Test suite
├── pyproject.toml          # Project configuration (Hatch)
├── README.md               # User documentation
├── CONTRIBUTING.md         # This file
├── CHANGELOG.md            # Version history
└── LICENSE                 # MIT License
```

## Design Principles

wn_edit follows these design principles to maintain compatibility with the [wn](https://github.com/goodmami/wn) library:

### 1. Use wn.lmf Data Structures

All data is stored using `wn.lmf` TypedDict-style dictionaries, not custom classes. This ensures:

- Direct compatibility with `wn.lmf.dump()` for export
- Direct compatibility with `wn.add_lexical_resource()` for database commits
- No translation layer needed

### 2. Correct Key Names

The `wn.lmf` module uses specific key names that differ from intuitive choices:

| What | Key Name | NOT |
|------|----------|-----|
| Lexical entries | `entries` | `lexical_entries` |
| Lemma text | `writtenForm` | `form` |
| Part of speech | `partOfSpeech` | `pos` |
| Relation type | `relType` | `rel_type` |

Always check the TypedDict definitions in `wn/lmf.py` when adding new features.

### 3. Import Constants from wn

Don't hardcode constants like relation types or POS tags. Import them from `wn.constants`:

```python
from wn import constants as wn_constants
SYNSET_RELATIONS = wn_constants.SYNSET_RELATIONS
```

### 4. Graceful Degradation

Use `HAS_WN` checks for features that require the wn package:

```python
if not HAS_WN:
    raise ImportError("The 'wn' package is required...")
```

## Adding New Features

### Adding a New Method to WordnetEditor

1. Add the method to `editor.py` in the appropriate section (Synset Operations, Entry Operations, etc.)

2. Follow the existing patterns:
   - Use type hints
   - Include a docstring with Args/Returns
   - Update internal indexes if needed (`_synset_by_id`, etc.)

3. Add tests in `test_editor.py`:
   - Create a new test method in the appropriate test class
   - Use the `editor` fixture for tests requiring a WordnetEditor instance

4. Update documentation:
   - Add to the API table in README.md
   - Update CHANGELOG.md

### Adding a New Helper Function

1. Add the function near the top of `editor.py` with other `make_*` functions

2. Export it in `__init__.py`

3. Add tests in `TestHelperFunctions`

4. Document in README.md

## Testing Guidelines

### Test Organization

Tests are organized by functionality:

- `TestHelperFunctions` - Tests for `make_*` helper functions
- `TestWordnetEditorCreate` - Tests for editor creation
- `TestWordnetEditorSynsets` - Tests for synset operations
- `TestWordnetEditorEntries` - Tests for entry/word operations
- `TestWordnetEditorExport` - Tests for export functionality
- `TestWordnetEditorMetadata` - Tests for metadata operations
- `TestWordnetEditorRoundTrip` - Integration tests for full workflows

### Fixtures

The `editor` fixture provides a fresh WordnetEditor for each test:

```python
@pytest.fixture
def editor():
    return WordnetEditor(
        create_new=True,
        lexicon_id="test-wn",
        label="Test WordNet",
        ...
    )
```

### Round-Trip Testing

When adding features that affect export/import, include round-trip tests:

1. Create data with WordnetEditor
2. Export to XML
3. Verify XML structure with ElementTree
4. Load back with `load_from_file()`
5. Verify data integrity

## Submitting Changes

1. Create a feature branch from `main`
2. Make your changes with clear commit messages
3. Ensure all tests pass: `hatch test`
4. Ensure code quality checks pass: `hatch fmt --check`
5. Update CHANGELOG.md
6. Submit a pull request

## Questions?

Open an issue on GitHub for questions or discussion.
