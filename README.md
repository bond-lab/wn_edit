# wn_edit

**An editing extension for the Python [wn](https://github.com/goodmami/wn) WordNet library**

[![PyPI link](https://img.shields.io/pypi/v/wn_edit.svg?style=flat-square)](https://pypi.org/project/wn_edit/)
[![Python Support](https://img.shields.io/pypi/pyversions/wn_edit.svg?style=flat-square)](https://pypi.org/project/wn_edit/)
[![License](https://img.shields.io/pypi/l/wn_edit.svg?style=flat-square)](https://opensource.org/licenses/MIT)

---

**wn_edit** extends the [wn](https://github.com/goodmami/wn) library with capabilities for creating, modifying, and exporting WordNet lexicons. It works directly with `wn.lmf` data structures, ensuring full compatibility with the wn ecosystem.

## Installation

```bash
pip install wn_edit
```

**Requirements:** Python 3.10+ and [wn](https://pypi.org/project/wn/) 0.9.0+

## Quick Start

### Creating a New WordNet

```python
from wn_edit import WordnetEditor

# Create a new lexicon from scratch
editor = WordnetEditor(
    create_new=True,
    lexicon_id='my-wordnet',
    label='My Custom WordNet',
    language='en',
    email='author@example.com',
    license='https://creativecommons.org/licenses/by/4.0/',
    version='1.0',
)

# Add synsets with words
animal = editor.create_synset(
    pos='n',
    definition='A living organism that feeds on organic matter',
    words=['animal', 'creature', 'beast'],
    examples=['Animals need food and water to survive.'],
)

dog = editor.create_synset(
    pos='n',
    definition='A domesticated carnivorous mammal',
    words=['dog', 'canine', 'hound'],
)

# Add relations between synsets
editor.add_synset_relation(dog['id'], animal['id'], 'hypernym')

# Export to WN-LMF XML
editor.export('my_wordnet.xml')
```

### Editing an Existing WordNet

```python
import wn
from wn_edit import WordnetEditor

# First, ensure the wordnet is in your database
wn.download('oewn:2024')

# Load it for editing
editor = WordnetEditor('oewn:2024')

# Add a new word to an existing synset
editor.add_word_to_synset('oewn-02084071-n', 'pupper')

# Create a new synset and link it
new_synset = editor.create_synset(
    pos='n',
    definition='A very good dog',
    words=['goodboy', 'good boy'],
)
editor.add_synset_relation(new_synset['id'], 'oewn-02084071-n', 'hypernym')

# Export the modified version
editor.set_version('2024-modified')
editor.export('oewn_modified.xml')
```

### Loading from XML File

```python
from wn_edit import WordnetEditor

# Load directly from a WN-LMF XML file (without adding to database)
editor = WordnetEditor.load_from_file('existing_wordnet.xml')

# Make modifications
editor.create_synset(pos='n', definition='A new concept', words=['newword'])

# Export
editor.export('modified_wordnet.xml')
```

## Features

### Synset Operations

```python
# Create a synset
synset = editor.create_synset(
    pos='n',                          # Part of speech: n, v, a, r, s
    definition='The definition',
    words=['word1', 'word2'],         # Optional: words to include
    examples=['An example sentence.'], # Optional: usage examples
    ili='i12345',                     # Optional: ILI identifier
)

# Modify a synset
editor.modify_synset(
    synset['id'],
    definition='Updated definition',
    add_examples=['Another example.'],
)

# Remove a synset
editor.remove_synset(synset['id'])

# Add relations
editor.add_synset_relation(source_id, target_id, 'hypernym')
editor.add_synset_relation(source_id, target_id, 'hyponym')
editor.add_synset_relation(source_id, target_id, 'similar')
# ... and many more relation types
```

### Entry/Word Operations

```python
# Add a word to an existing synset
editor.add_word_to_synset('synset-id', 'newword')

# Create a standalone entry (without synset association)
entry = editor.create_entry(
    lemma='word',
    pos='n',
    forms=['words', 'wording'],  # Optional: inflected forms
)

# Find entries by lemma
entries = editor.find_entries('dog')
entries_filtered = editor.find_entries('dog', pos='n')

# Remove an entry
editor.remove_entry(entry['id'])
```

### Metadata Operations

```python
# Get current metadata
metadata = editor.get_metadata()
print(metadata['version'], metadata['label'])

# Update metadata
editor.set_version('2.0')
editor.set_label('My WordNet (Extended Edition)')
editor.set_email('new@example.com')

# Or update multiple fields at once
editor.update_metadata(
    version='2.1',
    label='My WordNet v2.1',
    citation='Please cite as...',
)
```

### Validation

```python
# Validate before export (requires wn.validate)
errors = editor.validate()
if errors:
    print("Validation errors:", errors)

# Or validate automatically during export/commit
editor.export('output.xml', validate_first=True)
editor.commit(validate_first=True)
```

### Relation Types

The module uses standard WN-LMF relation types from `wn.constants`:

**Synset Relations:** `hypernym`, `hyponym`, `instance_hypernym`, `instance_hyponym`, `holonym`, `meronym`, `similar`, `also`, `attribute`, `causes`, `entails`, and [many more](https://globalwordnet.github.io/schemas/).

**Sense Relations:** `antonym`, `also`, `participle`, `pertainym`, `derivation`, `similar`, and others.

Non-standard relations trigger a warning by default:

```python
# Warning issued for non-standard relation
editor.add_synset_relation(s1, s2, 'my_custom_relation')

# Suppress warning if intentional
editor.add_synset_relation(s1, s2, 'my_custom_relation', validate=False)
```

## API Reference

### WordnetEditor

| Method | Description |
|--------|-------------|
| `WordnetEditor(lexicon_specifier)` | Load existing lexicon from database |
| `WordnetEditor(create_new=True, ...)` | Create new lexicon |
| `WordnetEditor.load_from_file(path)` | Load from WN-LMF XML file |
| `create_synset(pos, definition, ...)` | Create a new synset |
| `modify_synset(synset_id, ...)` | Modify an existing synset |
| `remove_synset(synset_id)` | Remove a synset |
| `add_synset_relation(src, tgt, rel)` | Add relation between synsets |
| `create_entry(lemma, pos, ...)` | Create a lexical entry |
| `add_word_to_synset(synset_id, word)` | Add word to synset |
| `find_entries(lemma, pos=None)` | Find entries by lemma |
| `remove_entry(entry_id)` | Remove an entry |
| `get_synset(synset_id)` | Get synset by ID |
| `stats()` | Get lexicon statistics |
| `get_metadata()` / `set_*()` | Metadata access/modification |
| `validate()` | Validate the lexicon |
| `export(path, validate_first=False)` | Export to WN-LMF XML |
| `commit(validate_first=False)` | Commit to wn database |

### Helper Functions

For building `wn.lmf`-compatible data structures directly:

```python
from wn_edit import (
    make_lexical_resource,
    make_lexicon,
    make_synset,
    make_lexical_entry,
    make_lemma,
    make_sense,
    make_definition,
    make_example,
    make_relation,
    make_form,
)
```

## Compatibility

**wn_edit** is designed to work seamlessly with the [wn](https://github.com/goodmami/wn) ecosystem:

- Uses `wn.lmf` TypedDict structures internally
- Exports via `wn.lmf.dump()` for valid WN-LMF XML
- Commits via `wn.add_lexical_resource()` for database integration
- Validates using `wn.validate` when available
- Uses relation types from `wn.constants`

## License

MIT License - see [LICENSE](LICENSE) for details.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development setup and guidelines.

## Citation

If you use wn_edit in your research, please also cite the wn library:

> Michael Wayne Goodman and Francis Bond. 2021. [Intrinsically Interlingual: The Wn Python Library for Wordnets](https://aclanthology.org/2021.gwc-1.12/) In *Proceedings of the 11th Global Wordnet Conference*, pages 100–107.
