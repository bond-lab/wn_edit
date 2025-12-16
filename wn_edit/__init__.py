"""
wn_edit - A modification add-on for the Python wn (WordNet) module

This module extends the wn library to allow editing, adding, and removing
entries in WordNet databases. It works by leveraging wn.lmf data structures
directly, ensuring compatibility and reducing code duplication.

Example usage:
    >>> import wn
    >>> from wn_edit import WordnetEditor
    >>> 
    >>> # Create an editor for a specific lexicon
    >>> editor = WordnetEditor('oewn:2024')
    >>> 
    >>> # Add a new word to an existing synset
    >>> editor.add_word_to_synset('oewn-00001740-n', 'newterm')
    >>> 
    >>> # Create a new synset
    >>> editor.create_synset(
    ...     pos='n',
    ...     definition='A test concept',
    ...     words=['testword1', 'testword2']
    ... )
    >>> 
    >>> # Commit changes to database
    >>> editor.commit()
    >>> 
    >>> # Or export using wn.lmf.dump()
    >>> editor.export('my_wordnet_extension.xml')

Design Philosophy:
    This module uses wn.lmf TypedDict structures directly rather than 
    defining parallel classes. This ensures:
    - Full compatibility with the wn module
    - Use of wn.lmf.dump() for export
    - Use of wn.add_lexical_resource() for database commits
    - Automatic benefit from wn updates/fixes
"""

from .editor import (
    WordnetEditor,
    # Helper functions to create wn.lmf-compatible dicts
    make_lexical_resource,
    make_lexicon,
    make_lexical_entry,
    make_lemma,
    make_sense,
    make_synset,
    make_definition,
    make_example,
    make_count,
    make_relation,
    make_form,
    # Validation helpers
    validate_pos,
    validate_count,
    validate_adjposition,
    HAS_WN,
    HAS_WN_VALIDATE,
    # Constants
    SYNSET_RELATIONS,
    SENSE_RELATIONS,
    PARTS_OF_SPEECH,
    ADJPOSITIONS,
)
from .version import __version__

__all__ = [
    'WordnetEditor',
    '__version__',
    # Helper functions
    'make_lexical_resource',
    'make_lexicon',
    'make_lexical_entry',
    'make_lemma',
    'make_sense',
    'make_synset',
    'make_definition',
    'make_example',
    'make_count',
    'make_relation',
    'make_form',
    # Validation helpers
    'validate_pos',
    'validate_count',
    'validate_adjposition',
    'HAS_WN',
    'HAS_WN_VALIDATE',
    # Constants
    'SYNSET_RELATIONS',
    'SENSE_RELATIONS',
    'PARTS_OF_SPEECH',
    'ADJPOSITIONS',
]
