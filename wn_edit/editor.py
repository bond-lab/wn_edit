"""
WordnetEditor - High-level interface for modifying WordNet databases.

This editor leverages wn.lmf data structures directly, ensuring full
compatibility with the wn module. It uses wn.lmf.dump() for export and
wn.add_lexical_resource() for committing to the database.

The wn.lmf module uses TypedDict-style dictionaries for its data structures:
- LexicalResource: {'lmf_version': str, 'lexicons': [...]}
- Lexicon: {'id': str, 'label': str, 'language': str, ...}
- LexicalEntry: {'id': str, 'lemma': {...}, 'senses': [...], ...}
- Synset: {'id': str, 'pos': str, 'definitions': [...], ...}
- etc.

This editor works directly with these structures.
"""

from typing import Optional, List, Dict, Any, Union
from pathlib import Path
import uuid

try:
    import wn
    from wn import lmf
    HAS_WN = True
except ImportError:
    HAS_WN = False
    wn = None
    lmf = None


# Default LMF version
DEFAULT_LMF_VERSION = '1.4'


def make_lexical_resource(
    lexicons: List[Dict],
    lmf_version: str = DEFAULT_LMF_VERSION,
) -> Dict:
    """Create a LexicalResource dictionary."""
    return {
        'lmf_version': lmf_version,
        'lexicons': lexicons,
    }


def make_lexicon(
    id: str,
    label: str,
    language: str,
    email: str,
    license: str,
    version: str,
    url: Optional[str] = None,
    citation: Optional[str] = None,
    entries: Optional[List[Dict]] = None,
    synsets: Optional[List[Dict]] = None,
    frames: Optional[List[Dict]] = None,
    meta: Optional[Dict] = None,
) -> Dict:
    """Create a Lexicon dictionary.
    
    Note: Uses 'entries' (not 'entries') to match wn.lmf structure.
    """
    lex = {
        'id': id,
        'label': label,
        'language': language,
        'email': email,
        'license': license,
        'version': version,
        'entries': entries or [],
        'synsets': synsets or [],
    }
    if url:
        lex['url'] = url
    if citation:
        lex['citation'] = citation
    if frames:
        lex['frames'] = frames
    if meta:
        lex['meta'] = meta
    return lex


def make_lexical_entry(
    id: str,
    lemma: Dict,
    forms: Optional[List[Dict]] = None,
    senses: Optional[List[Dict]] = None,
    syntactic_behaviours: Optional[List[str]] = None,
    meta: Optional[Dict] = None,
) -> Dict:
    """Create a LexicalEntry dictionary."""
    entry = {
        'id': id,
        'lemma': lemma,
        'senses': senses or [],
    }
    if forms:
        entry['forms'] = forms
    if syntactic_behaviours:
        entry['syntactic_behaviours'] = syntactic_behaviours
    if meta:
        entry['meta'] = meta
    return entry


def make_lemma(
    written_form: str,
    pos: str,
    script: Optional[str] = None,
    pronunciations: Optional[List[Dict]] = None,
    tags: Optional[List[Dict]] = None,
) -> Dict:
    """Create a Lemma dictionary.
    
    Note: Uses 'writtenForm' and 'partOfSpeech' to match wn.lmf structure.
    """
    lemma = {
        'writtenForm': written_form,
        'partOfSpeech': pos,
    }
    if script:
        lemma['script'] = script
    if pronunciations:
        lemma['pronunciations'] = pronunciations
    if tags:
        lemma['tags'] = tags
    return lemma


def make_sense(
    id: str,
    synset: str,
    relations: Optional[List[Dict]] = None,
    examples: Optional[List[Dict]] = None,
    counts: Optional[List[Dict]] = None,
    adjposition: Optional[str] = None,
    subcat: Optional[List[str]] = None,
    meta: Optional[Dict] = None,
) -> Dict:
    """Create a Sense dictionary."""
    sense = {
        'id': id,
        'synset': synset,
    }
    if relations:
        sense['relations'] = relations
    if examples:
        sense['examples'] = examples
    if counts:
        sense['counts'] = counts
    if adjposition:
        sense['adjposition'] = adjposition
    if subcat:
        sense['subcat'] = subcat
    if meta:
        sense['meta'] = meta
    return sense


def make_synset(
    id: str,
    pos: str,
    ili: Optional[str] = None,
    definitions: Optional[List[Dict]] = None,
    ili_definition: Optional[Dict] = None,
    relations: Optional[List[Dict]] = None,
    examples: Optional[List[Dict]] = None,
    meta: Optional[Dict] = None,
) -> Dict:
    """Create a Synset dictionary.
    
    Note: The 'ili' key is always included (defaults to empty string)
    because wn.lmf.dump() requires it to be present.
    Uses 'partOfSpeech' to match wn.lmf structure.
    """
    synset = {
        'id': id,
        'partOfSpeech': pos,
        'ili': ili or '',  # Required by wn.lmf.dump()
    }
    if definitions:
        synset['definitions'] = definitions
    if ili_definition:
        synset['ili_definition'] = ili_definition
    if relations:
        synset['relations'] = relations
    if examples:
        synset['examples'] = examples
    if meta:
        synset['meta'] = meta
    return synset


def make_definition(text: str, language: Optional[str] = None, source_sense: Optional[str] = None, meta: Optional[Dict] = None) -> Dict:
    """Create a Definition dictionary."""
    d = {'text': text}
    if language:
        d['language'] = language
    if source_sense:
        d['source_sense'] = source_sense
    if meta:
        d['meta'] = meta
    return d


def make_example(text: str, language: Optional[str] = None, meta: Optional[Dict] = None) -> Dict:
    """Create an Example dictionary."""
    e = {'text': text}
    if language:
        e['language'] = language
    if meta:
        e['meta'] = meta
    return e


def make_relation(target: str, rel_type: str, meta: Optional[Dict] = None) -> Dict:
    """Create a Relation dictionary (works for both SynsetRelation and SenseRelation).
    
    Note: Uses 'relType' (camelCase) as required by wn.lmf.dump().
    """
    r = {'target': target, 'relType': rel_type}
    if meta:
        r['meta'] = meta
    return r


def make_form(written_form: str, script: Optional[str] = None, tags: Optional[List[Dict]] = None) -> Dict:
    """Create a Form dictionary.
    
    Note: Uses 'writtenForm' to match wn.lmf structure.
    """
    f = {'writtenForm': written_form}
    if script:
        f['script'] = script
    if tags:
        f['tags'] = tags
    return f


class WordnetEditor:
    """
    High-level editor for modifying WordNet databases.
    
    This class uses wn.lmf data structures (TypedDict-style dictionaries)
    directly, ensuring full compatibility with the wn module.
    
    Key methods:
    - wn.lmf.load() - Load WN-LMF XML into a LexicalResource dict
    - wn.lmf.dump() - Write LexicalResource dict to XML
    - wn.add_lexical_resource() - Add in-memory resource to database
    
    Example:
        >>> import wn
        >>> from wn_edit import WordnetEditor
        >>> 
        >>> wn.download('oewn:2024')
        >>> editor = WordnetEditor('oewn:2024')
        >>> 
        >>> # Create a new synset
        >>> synset = editor.create_synset(
        ...     pos='n',
        ...     definition='A test concept',
        ...     words=['testword']
        ... )
        >>> 
        >>> # Export using wn.lmf.dump()
        >>> editor.export('my_extension.xml')
    """
    
    def __init__(
        self,
        lexicon_specifier: Optional[str] = None,
        create_new: bool = False,
        lexicon_id: Optional[str] = None,
        label: Optional[str] = None,
        language: str = 'en',
        email: str = 'user@example.com',
        license: str = 'https://creativecommons.org/licenses/by/4.0/',
        version: str = '1.0',
        lmf_version: str = DEFAULT_LMF_VERSION,
    ):
        """
        Initialize the WordnetEditor.
        
        Args:
            lexicon_specifier: Specifier for existing lexicon (e.g., 'oewn:2024')
            create_new: If True, create a new empty lexicon
            lexicon_id: ID for new lexicon (required if create_new=True)
            label: Label for new lexicon
            language: Language code (BCP-47)
            email: Contact email
            license: License URL
            version: Version string
            lmf_version: WN-LMF version (default: 1.4)
        """
        if not HAS_WN:
            raise ImportError(
                "The 'wn' package is required. Install with: pip install wn"
            )
        
        self._base_lexicon_specifier = lexicon_specifier
        
        if create_new:
            if not lexicon_id:
                raise ValueError("lexicon_id is required when create_new=True")
            self._resource = self._create_new_resource(
                lexicon_id=lexicon_id,
                label=label or lexicon_id,
                language=language,
                email=email,
                license=license,
                version=version,
                lmf_version=lmf_version,
            )
        elif lexicon_specifier:
            self._resource = self._load_from_database(lexicon_specifier)
        else:
            raise ValueError("Either lexicon_specifier or create_new must be provided")
        
        # Quick access to the primary lexicon
        self._lexicon = self._resource['lexicons'][0] if self._resource['lexicons'] else None
        
        # Build indexes for fast lookup
        self._rebuild_indexes()
    
    def _create_new_resource(
        self,
        lexicon_id: str,
        label: str,
        language: str,
        email: str,
        license: str,
        version: str,
        lmf_version: str,
    ) -> Dict:
        """Create a new empty LexicalResource with one Lexicon."""
        lexicon = make_lexicon(
            id=lexicon_id,
            label=label,
            language=language,
            email=email,
            license=license,
            version=version,
        )
        return make_lexical_resource([lexicon], lmf_version)
    
    def _load_from_database(self, specifier: str) -> Dict:
        """
        Load a lexicon from the wn database into an editable LexicalResource.
        
        This exports the lexicon to a temp file, then loads it with wn.lmf.load().
        """
        import tempfile
        import os
        
        # Get lexicons from database
        wordnet = wn.Wordnet(specifier)
        lexicons = wordnet.lexicons()
        
        if not lexicons:
            raise ValueError(f"No lexicons found for specifier: {specifier}")
        
        # Export to temp file
        with tempfile.NamedTemporaryFile(
            mode='w', suffix='.xml', delete=False
        ) as f:
            temp_path = f.name
        
        try:
            wn.export(lexicons, temp_path)
            resource = lmf.load(temp_path)
            return resource
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)
    
    def _rebuild_indexes(self) -> None:
        """Build indexes for fast lookup of entries and synsets.
        
        Note: wn.lmf.load() may use 'entries' while we use 'entries'.
        This method handles both key names.
        """
        self._entry_by_id: Dict[str, Dict] = {}
        self._synset_by_id: Dict[str, Dict] = {}
        self._entries_by_lemma: Dict[str, List[Dict]] = {}
        
        if self._lexicon:
            # Handle both 'entries' (our format) and 'entries' (wn.lmf.load format)
            entries = self._lexicon.get('entries') or self._lexicon.get('entries', [])
            
            for entry in entries:
                self._entry_by_id[entry['id']] = entry
                lemma_form = entry['lemma']['writtenForm']
                if lemma_form not in self._entries_by_lemma:
                    self._entries_by_lemma[lemma_form] = []
                self._entries_by_lemma[lemma_form].append(entry)
            
            for synset in self._lexicon.get('synsets', []):
                self._synset_by_id[synset['id']] = synset
    
    def _generate_id(self, prefix: str, suffix: str = '') -> str:
        """Generate a unique ID for a new entry."""
        unique = uuid.uuid4().hex[:8]
        lex_id = self._lexicon['id'] if self._lexicon else 'custom'
        parts = [lex_id, prefix, unique]
        if suffix:
            parts.append(suffix)
        return '-'.join(parts)
    
    # =========================================================================
    # Properties
    # =========================================================================
    
    @property
    def resource(self) -> Dict:
        """The underlying LexicalResource dictionary."""
        return self._resource
    
    @property
    def lexicon(self) -> Dict:
        """The primary Lexicon dictionary being edited."""
        return self._lexicon
    
    # =========================================================================
    # Lexicon Metadata Operations
    # =========================================================================
    
    def set_version(self, version: str) -> None:
        """Set the lexicon version."""
        self._lexicon['version'] = version
    
    def set_label(self, label: str) -> None:
        """Set the lexicon label."""
        self._lexicon['label'] = label
    
    def set_email(self, email: str) -> None:
        """Set the contact email."""
        self._lexicon['email'] = email
    
    def set_license(self, license: str) -> None:
        """Set the license URL."""
        self._lexicon['license'] = license
    
    def set_url(self, url: str) -> None:
        """Set the lexicon URL."""
        self._lexicon['url'] = url
    
    def set_citation(self, citation: str) -> None:
        """Set the citation text."""
        self._lexicon['citation'] = citation
    
    def update_metadata(
        self,
        version: Optional[str] = None,
        label: Optional[str] = None,
        email: Optional[str] = None,
        license: Optional[str] = None,
        url: Optional[str] = None,
        citation: Optional[str] = None,
    ) -> None:
        """
        Update multiple lexicon metadata fields at once.
        
        Only provided (non-None) values are updated.
        
        Args:
            version: Version string (e.g., '1.1', '2.0')
            label: Human-readable label
            email: Contact email
            license: License URL
            url: Lexicon URL
            citation: Citation text
            
        Example:
            >>> editor.update_metadata(
            ...     version='1.1',
            ...     label='My WordNet (Extended)',
            ... )
        """
        if version is not None:
            self._lexicon['version'] = version
        if label is not None:
            self._lexicon['label'] = label
        if email is not None:
            self._lexicon['email'] = email
        if license is not None:
            self._lexicon['license'] = license
        if url is not None:
            self._lexicon['url'] = url
        if citation is not None:
            self._lexicon['citation'] = citation
    
    def get_metadata(self) -> Dict[str, str]:
        """
        Get the lexicon metadata.
        
        Returns:
            Dictionary with id, label, language, version, email, license, url, citation
        """
        return {
            'id': self._lexicon.get('id', ''),
            'label': self._lexicon.get('label', ''),
            'language': self._lexicon.get('language', ''),
            'version': self._lexicon.get('version', ''),
            'email': self._lexicon.get('email', ''),
            'license': self._lexicon.get('license', ''),
            'url': self._lexicon.get('url', ''),
            'citation': self._lexicon.get('citation', ''),
        }
    
    # =========================================================================
    # Synset Operations
    # =========================================================================
    
    def create_synset(
        self,
        pos: str,
        definition: Optional[str] = None,
        definitions: Optional[List[str]] = None,
        examples: Optional[List[str]] = None,
        words: Optional[List[str]] = None,
        ili: Optional[str] = None,
        synset_id: Optional[str] = None,
    ) -> Dict:
        """
        Create a new synset and optionally add words to it.
        
        Args:
            pos: Part of speech ('n', 'v', 'a', 'r', 's')
            definition: Single definition text
            definitions: List of definition texts
            examples: List of example sentences
            words: List of word forms to add to the synset
            ili: Interlingual Index (optional)
            synset_id: Custom ID (auto-generated if not provided)
        
        Returns:
            The created synset dictionary
        """
        if synset_id is None:
            synset_id = self._generate_id('synset', pos)
        
        # Build definitions list
        defs = []
        if definition:
            defs.append(make_definition(definition))
        if definitions:
            defs.extend(make_definition(d) for d in definitions)
        
        # Build examples list
        exs = []
        if examples:
            exs.extend(make_example(e) for e in examples)
        
        synset = make_synset(
            id=synset_id,
            pos=pos,
            ili=ili,
            definitions=defs if defs else None,
            examples=exs if exs else None,
        )
        
        # Add to lexicon
        self._lexicon['synsets'].append(synset)
        self._synset_by_id[synset_id] = synset
        
        # Add words if provided
        if words:
            for word in words:
                self.add_word_to_synset(synset_id, word, pos)
        
        return synset
    
    def get_synset(self, synset_id: str) -> Optional[Dict]:
        """Get a synset by ID."""
        return self._synset_by_id.get(synset_id)
    
    def modify_synset(
        self,
        synset_id: str,
        definition: Optional[str] = None,
        add_definitions: Optional[List[str]] = None,
        add_examples: Optional[List[str]] = None,
        ili: Optional[str] = None,
    ) -> Dict:
        """Modify an existing synset."""
        synset = self._synset_by_id.get(synset_id)
        if synset is None:
            raise KeyError(f"Synset not found: {synset_id}")
        
        if definition is not None:
            synset['definitions'] = [make_definition(definition)]
        
        if add_definitions:
            if 'definitions' not in synset:
                synset['definitions'] = []
            synset['definitions'].extend(make_definition(d) for d in add_definitions)
        
        if add_examples:
            if 'examples' not in synset:
                synset['examples'] = []
            synset['examples'].extend(make_example(e) for e in add_examples)
        
        if ili is not None:
            synset['ili'] = ili
        
        return synset
    
    def remove_synset(self, synset_id: str) -> None:
        """Remove a synset and all senses pointing to it."""
        synset = self._synset_by_id.get(synset_id)
        if synset is None:
            raise KeyError(f"Synset not found: {synset_id}")
        
        # Remove from lexicon
        self._lexicon['synsets'] = [
            s for s in self._lexicon['synsets'] if s['id'] != synset_id
        ]
        del self._synset_by_id[synset_id]
        
        # Remove senses pointing to this synset
        for entry in self._lexicon['entries']:
            entry['senses'] = [
                s for s in entry.get('senses', []) if s['synset'] != synset_id
            ]
    
    def add_synset_relation(
        self,
        source_id: str,
        target_id: str,
        rel_type: str,
    ) -> None:
        """Add a relation between synsets."""
        synset = self._synset_by_id.get(source_id)
        if synset is None:
            raise KeyError(f"Source synset not found: {source_id}")
        
        if 'relations' not in synset:
            synset['relations'] = []
        
        synset['relations'].append(make_relation(target_id, rel_type))
    
    # =========================================================================
    # Word/Entry Operations
    # =========================================================================
    
    def create_entry(
        self,
        lemma: str,
        pos: str,
        entry_id: Optional[str] = None,
        forms: Optional[List[str]] = None,
    ) -> Dict:
        """Create a new lexical entry (word)."""
        if entry_id is None:
            safe_lemma = lemma.replace(' ', '_')
            entry_id = self._generate_id(safe_lemma, pos)
        
        form_dicts = None
        if forms:
            form_dicts = [make_form(f) for f in forms]
        
        entry = make_lexical_entry(
            id=entry_id,
            lemma=make_lemma(lemma, pos),
            forms=form_dicts,
        )
        
        self._lexicon['entries'].append(entry)
        self._entry_by_id[entry_id] = entry
        
        if lemma not in self._entries_by_lemma:
            self._entries_by_lemma[lemma] = []
        self._entries_by_lemma[lemma].append(entry)
        
        return entry
    
    def get_entry(self, entry_id: str) -> Optional[Dict]:
        """Get an entry by ID."""
        return self._entry_by_id.get(entry_id)
    
    def find_entries(self, lemma: str, pos: Optional[str] = None) -> List[Dict]:
        """Find entries by lemma and optionally part of speech."""
        entries = self._entries_by_lemma.get(lemma, [])
        if pos:
            entries = [e for e in entries if e['lemma']['partOfSpeech'] == pos]
        return entries
    
    def add_word_to_synset(
        self,
        synset_id: str,
        lemma: str,
        pos: Optional[str] = None,
    ) -> Dict:
        """Add a word to an existing synset."""
        synset = self._synset_by_id.get(synset_id)
        if synset is None:
            raise KeyError(f"Synset not found: {synset_id}")
        
        pos = pos or synset['partOfSpeech']
        
        # Find or create entry
        existing = self.find_entries(lemma, pos)
        if existing:
            entry = existing[0]
        else:
            entry = self.create_entry(lemma, pos)
        
        # Check if sense already exists
        has_sense = any(s['synset'] == synset_id for s in entry.get('senses', []))
        if not has_sense:
            sense_id = f"{entry['id']}-{synset_id}"
            sense = make_sense(id=sense_id, synset=synset_id)
            entry['senses'].append(sense)
        
        return entry
    
    def remove_entry(self, entry_id: str) -> None:
        """Remove a lexical entry."""
        entry = self._entry_by_id.get(entry_id)
        if entry is None:
            raise KeyError(f"Entry not found: {entry_id}")
        
        self._lexicon['entries'] = [
            e for e in self._lexicon['entries'] if e['id'] != entry_id
        ]
        del self._entry_by_id[entry_id]
        
        lemma = entry['lemma']['writtenForm']
        if lemma in self._entries_by_lemma:
            self._entries_by_lemma[lemma] = [
                e for e in self._entries_by_lemma[lemma] if e['id'] != entry_id
            ]
    
    def add_sense_relation(
        self,
        source_sense_id: str,
        target_id: str,
        rel_type: str,
    ) -> None:
        """Add a relation from a sense."""
        # Find the sense
        for entry in self._lexicon['entries']:
            for sense in entry.get('senses', []):
                if sense['id'] == source_sense_id:
                    if 'relations' not in sense:
                        sense['relations'] = []
                    sense['relations'].append(make_relation(target_id, rel_type))
                    return
        
        raise KeyError(f"Sense not found: {source_sense_id}")
    
    # =========================================================================
    # Export and Commit
    # =========================================================================
    
    def export(self, filepath: Union[str, Path]) -> None:
        """
        Export the lexicon to a WN-LMF XML file using wn.lmf.dump().
        
        Args:
            filepath: Output file path
        """
        filepath = Path(filepath)
        lmf.dump(self._resource, filepath)
    
    def commit(self) -> None:
        """
        Commit changes to the wn database using wn.add_lexical_resource().
        """
        wn.add_lexical_resource(self._resource)
    
    # =========================================================================
    # Statistics and Info
    # =========================================================================
    
    def stats(self) -> Dict[str, int]:
        """Get statistics about the lexicon."""
        # Handle both 'entries' (our format) and 'entries' (wn.lmf.load format)
        entries = self._lexicon.get('entries') or self._lexicon.get('entries', [])
        num_senses = sum(len(e.get('senses', [])) for e in entries)
        return {
            'synsets': len(self._lexicon.get('synsets', [])),
            'entries': len(entries),
            'senses': num_senses,
        }
    
    def __repr__(self) -> str:
        stats = self.stats()
        return (
            f"WordnetEditor(lexicon='{self._lexicon['id']}', "
            f"synsets={stats['synsets']}, entries={stats['entries']})"
        )
    
    # =========================================================================
    # Class Methods for Loading
    # =========================================================================
    
    @classmethod
    def load_from_file(cls, filepath: Union[str, Path]) -> 'WordnetEditor':
        """
        Load a WordnetEditor from a WN-LMF XML file.
        
        This uses wn.lmf.load() to read the file and creates an editor
        for modifying its contents.
        
        Args:
            filepath: Path to the WN-LMF XML file
            
        Returns:
            A WordnetEditor instance with the loaded content
            
        Example:
            >>> editor = WordnetEditor.load_from_file('my_wordnet.xml')
            >>> editor.create_synset(pos='n', definition='New concept')
            >>> editor.export('my_wordnet_v2.xml')
        """
        filepath = Path(filepath)
        if not filepath.exists():
            raise FileNotFoundError(f"File not found: {filepath}")
        
        resource = lmf.load(filepath)
        
        if not resource.get('lexicons'):
            raise ValueError(f"No lexicons found in file: {filepath}")
        
        # Create a minimal editor and replace its resource
        lexicon = resource['lexicons'][0]
        editor = cls(
            create_new=True,
            lexicon_id=lexicon['id'],
            label=lexicon.get('label', lexicon['id']),
            language=lexicon.get('language', 'en'),
            email=lexicon.get('email', 'unknown@example.com'),
            license=lexicon.get('license', ''),
            version=lexicon.get('version', '1.0'),
        )
        
        # Replace with the loaded resource
        editor._resource = resource
        editor._lexicon = lexicon
        editor._rebuild_indexes()
        
        return editor
