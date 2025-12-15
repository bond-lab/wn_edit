# wn_edit

A modification add-on for the Python [wn](https://github.com/goodmami/wn) (WordNet) module that enables editing, adding, and removing entries in WordNet databases.

## Design Philosophy

This module is designed to work **with** the `wn` module, not parallel to it. It:

- Uses `wn.lmf` TypedDict structures directly (dictionaries with keys like `'id'`, `'lemma'`, `'senses'`, etc.)
- Uses `wn.lmf.dump()` for XML export
- Uses `wn.add_lexical_resource()` for database commits  
- Uses `wn.lmf.load()` to read existing lexicons
- Benefits automatically from `wn` updates and bug fixes
- Ensures full compatibility with the WN-LMF standard

## Installation

```bash
pip install wn_edit
```

Requires the `wn` package:

```bash
pip install wn
```

## Quick Start

```python
import wn
from wn_edit import WordnetEditor

# Ensure a wordnet is installed
wn.download('oewn:2024')

# Create an editor for an existing lexicon
editor = WordnetEditor('oewn:2024')

# Create a new synset with words
synset = editor.create_synset(
    pos='n',
    definition='A fictional example concept for testing',
    words=['exampleword', 'testterm'],
    examples=['This is an exampleword.']
)

# Add a word to an existing synset
editor.add_word_to_synset('oewn-00001740-n', 'newsynonym')

# Add a relation
editor.add_synset_relation(
    source_id=synset.id,
    target_id='oewn-00001740-n',
    rel_type='hypernym'
)

# Export changes
editor.export('my_wordnet_extension.xml')

# Or commit directly to the wn database
editor.commit()
```

## Creating a New Lexicon

```python
from wn_edit import WordnetEditor

# Create a brand new lexicon
editor = WordnetEditor(
    create_new=True,
    lexicon_id='my-wordnet',
    label='My Custom WordNet',
    language='en',
    email='me@example.com'
)

# Add content
synset = editor.create_synset(
    pos='n',
    definition='A new concept',
    words=['newword']
)

# Export
editor.export('my_wordnet.xml')
```

## Accessing wn.lmf Structures Directly

Since `wn_edit` uses `wn.lmf` TypedDict structures, you have full access to the underlying data:

```python
editor = WordnetEditor('oewn:2024')

# Access the LexicalResource dict
resource = editor.resource  # {'lmf_version': '1.4', 'lexicons': [...]}

# Access the Lexicon dict
lexicon = editor.lexicon  # {'id': ..., 'label': ..., 'synsets': [...], ...}

# Work with the dict structures directly
for synset in lexicon['synsets']:
    print(synset['id'], synset.get('definitions', []))

# Use helper functions to create compatible dicts
from wn_edit import make_definition, make_synset

synset = editor.get_synset('some-synset-id')
synset['definitions'].append(make_definition('Another definition'))
```

## API Reference

### WordnetEditor

#### Constructor

```python
WordnetEditor(
    lexicon_specifier: str = None,  # e.g., 'oewn:2024'
    create_new: bool = False,
    lexicon_id: str = None,
    label: str = None,
    language: str = 'en',
    email: str = 'user@example.com',
    license: str = 'https://creativecommons.org/licenses/by/4.0/',
    version: str = '1.0'
)
```

#### Properties

- `resource` - The underlying `wn.lmf.LexicalResource`
- `lexicon` - The primary `wn.lmf.Lexicon` being edited

#### Synset Methods

- `create_synset(pos, definition=None, definitions=None, examples=None, words=None, ili=None)` - Create a new synset
- `get_synset(synset_id)` - Get a synset by ID
- `modify_synset(synset_id, definition=None, add_definitions=None, add_examples=None, ili=None)` - Modify a synset
- `remove_synset(synset_id)` - Remove a synset

#### Entry/Word Methods

- `create_entry(lemma, pos, forms=None)` - Create a new lexical entry
- `get_entry(entry_id)` - Get an entry by ID
- `find_entries(lemma, pos=None)` - Find entries by lemma
- `add_word_to_synset(synset_id, lemma, pos=None)` - Add a word to a synset
- `remove_entry(entry_id)` - Remove an entry

#### Relation Methods

- `add_synset_relation(source_id, target_id, rel_type)` - Add a synset relation
- `add_sense_relation(source_sense_id, target_id, rel_type)` - Add a sense relation

#### Export/Commit

- `export(filepath, version='1.4')` - Export to WN-LMF XML
- `commit()` - Commit changes to the wn database
- `stats()` - Get statistics about the lexicon

### Relation Types

Common synset relation types (from WN-LMF):
- `hypernym`, `hyponym` - Taxonomic relations
- `mero_part`, `holo_part` - Part meronymy/holonymy
- `mero_member`, `holo_member` - Member meronymy/holonymy
- `similar`, `also` - Similarity relations
- `domain_topic`, `domain_region` - Domain relations
- `antonym` - Antonymy

Common sense relation types:
- `antonym` - Opposite meaning
- `similar`, `also` - Similarity
- `pertainym`, `derivation` - Morphological relations

## Compatibility

This module uses `wn.lmf` data structures directly, so:

- Any `LexicalResource` dict from `wn.lmf.load()` can be edited
- Exports via `wn.lmf.dump()` are fully compatible with WN-LMF tools
- `wn.add_lexical_resource()` works directly with the edited resource
- Updates to `wn` are automatically available

## License

MIT License

## See Also

- [wn](https://github.com/goodmami/wn) - The Python WordNet library this extends
- [WN-LMF Schema](https://globalwordnet.github.io/schemas/) - The standard format used
- [Open English WordNet](https://en-word.net/) - A recommended wordnet to use
