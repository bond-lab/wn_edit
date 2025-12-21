"""Tests for wn_edit.editor module.

These tests verify that:
1. Helper functions create properly structured wn.lmf-compatible dicts
2. WordnetEditor can create and manipulate lexicons
3. Export uses wn.lmf.dump() correctly
4. The data structures are compatible with wn.add_lexical_resource()

Note: Some tests require the `wn` package to be installed. Tests that
can run without `wn` are marked separately.
"""

import pytest
from pathlib import Path

# Import helper functions (these don't require wn)
from wn_edit.editor import (
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
    validate_pos,
    validate_count,
    PARTS_OF_SPEECH,
    HAS_WN,
)

# Skip tests that require wn if it's not installed
requires_wn = pytest.mark.skipif(not HAS_WN, reason="wn package not installed")


class TestValidation:
    """Tests for validation helper functions."""
    
    def test_validate_pos_valid(self):
        """Test that valid POS values pass validation."""
        for pos in ['n', 'v', 'a', 'r', 's']:
            validate_pos(pos)  # Should not raise
    
    def test_validate_pos_invalid(self):
        """Test that invalid POS values raise ValueError."""
        with pytest.raises(ValueError) as exc_info:
            validate_pos('invalid_pos_value')
        assert "Invalid part of speech: 'invalid_pos_value'" in str(exc_info.value)
        assert "Must be one of:" in str(exc_info.value)
    
    def test_validate_pos_custom_context(self):
        """Test custom context in validation error message."""
        with pytest.raises(ValueError) as exc_info:
            validate_pos('invalid', "synset part of speech")
        assert "Invalid synset part of speech: 'invalid'" in str(exc_info.value)
    
    def test_validate_count_valid(self):
        """Test that valid count values pass validation."""
        assert validate_count(0) == 0
        assert validate_count(42) == 42
        assert validate_count("100") == 100  # String convertible to int
    
    def test_validate_count_invalid_type(self):
        """Test that non-integer values raise TypeError."""
        with pytest.raises(TypeError) as exc_info:
            validate_count("not a number")
        assert "Must be an integer" in str(exc_info.value)
    
    def test_validate_count_negative(self):
        """Test that negative counts raise ValueError."""
        with pytest.raises(ValueError) as exc_info:
            validate_count(-1)
        assert "Must be non-negative" in str(exc_info.value)
    
    def test_parts_of_speech_constant(self):
        """Test PARTS_OF_SPEECH contains expected values."""
        # These are the standard WordNet POS tags that should always be present
        assert 'n' in PARTS_OF_SPEECH  # noun
        assert 'v' in PARTS_OF_SPEECH  # verb
        assert 'a' in PARTS_OF_SPEECH  # adjective
        assert 'r' in PARTS_OF_SPEECH  # adverb
        # 's' (satellite adjective) may or may not be present depending on wn version
        # Just verify we have at least the core 4
        assert len(PARTS_OF_SPEECH) >= 4


class TestHelperFunctions:
    """Tests for the helper functions that create wn.lmf-compatible dicts."""
    
    def test_make_definition(self):
        """Test creating a definition dict."""
        d = make_definition("A test definition")
        assert d == {"text": "A test definition", "meta": None}
        
        d = make_definition("Another definition", language="en")
        assert d == {"text": "Another definition", "language": "en", "meta": None}
    
    def test_make_example(self):
        """Test creating an example dict."""
        e = make_example("This is an example sentence.")
        assert e == {"text": "This is an example sentence.", "meta": None}
        
        e = make_example("Another example", language="en")
        assert e == {"text": "Another example", "language": "en", "meta": None}
    
    def test_make_relation(self):
        """Test creating a relation dict."""
        r = make_relation("target-synset-id", "hypernym")
        assert r == {"target": "target-synset-id", "relType": "hypernym", "meta": None}
    
    def test_make_lemma(self):
        """Test creating a lemma dict."""
        lemma = make_lemma("dog", "n")
        assert lemma == {"writtenForm": "dog", "partOfSpeech": "n"}
        
        lemma = make_lemma("café", "n", script="Latn")
        assert lemma["writtenForm"] == "café"
        assert lemma["partOfSpeech"] == "n"
        assert lemma["script"] == "Latn"
    
    def test_make_lemma_invalid_pos(self):
        """Test that make_lemma rejects invalid POS."""
        with pytest.raises(ValueError) as exc_info:
            make_lemma("word", "invalid_pos")
        assert "Invalid part of speech" in str(exc_info.value)
    
    def test_make_form(self):
        """Test creating a form dict."""
        f = make_form("dogs")
        assert f == {"writtenForm": "dogs"}
        
        f = make_form("ran", tags=[{"tag": "past"}])
        assert f["writtenForm"] == "ran"
        assert f["tags"] == [{"tag": "past"}]
    
    def test_make_sense(self):
        """Test creating a sense dict."""
        s = make_sense("sense-001", "synset-001")
        assert s == {"id": "sense-001", "synset": "synset-001", "meta": None}
        
        s = make_sense(
            "sense-002",
            "synset-002",
            relations=[make_relation("other-sense", "antonym")],
        )
        assert s["id"] == "sense-002"
        assert s["synset"] == "synset-002"
        assert s["meta"] is None
        assert len(s["relations"]) == 1
        assert s["relations"][0]["relType"] == "antonym"
    
    def test_make_synset(self):
        """Test creating a synset dict."""
        ss = make_synset("synset-001", "n")
        assert ss == {"id": "synset-001", "partOfSpeech": "n", "ili": "", "meta": None}
        
        ss = make_synset(
            "synset-002",
            "v",
            definitions=[make_definition("To do something")],
            examples=[make_example("I did something.")],
            ili="i12345",
        )
        assert ss["id"] == "synset-002"
        assert ss["partOfSpeech"] == "v"
        assert ss["ili"] == "i12345"
        assert ss["meta"] is None
        assert len(ss["definitions"]) == 1
        assert len(ss["examples"]) == 1
    
    def test_make_synset_invalid_pos(self):
        """Test that make_synset rejects invalid POS."""
        with pytest.raises(ValueError) as exc_info:
            make_synset("synset-001", "noun")  # Should be 'n', not 'noun'
        assert "Invalid part of speech" in str(exc_info.value)
    
    def test_make_count(self):
        """Test creating a count dict."""
        c = make_count(42)
        assert c == {"value": 42, "meta": None}
        
        c = make_count(0, meta={"source": "corpus"})
        assert c == {"value": 0, "meta": {"source": "corpus"}}
    
    def test_make_count_from_string(self):
        """Test that make_count accepts string integers."""
        c = make_count("100")
        assert c == {"value": 100, "meta": None}
    
    def test_make_count_invalid(self):
        """Test that make_count rejects invalid values."""
        with pytest.raises(TypeError):
            make_count("not a number")
        
        with pytest.raises(ValueError):
            make_count(-5)
    
    def test_make_lexical_entry(self):
        """Test creating a lexical entry dict."""
        entry = make_lexical_entry(
            "entry-001",
            make_lemma("dog", "n"),
        )
        assert entry["id"] == "entry-001"
        assert entry["lemma"]["writtenForm"] == "dog"
        assert entry["senses"] == []
        assert entry["meta"] is None
        
        entry = make_lexical_entry(
            "entry-002",
            make_lemma("run", "v"),
            forms=[make_form("ran"), make_form("running")],
            senses=[make_sense("sense-001", "synset-001")],
        )
        assert len(entry["forms"]) == 2
        assert len(entry["senses"]) == 1
    
    def test_make_lexicon(self):
        """Test creating a lexicon dict."""
        lex = make_lexicon(
            id="test-wn",
            label="Test WordNet",
            language="en",
            email="test@example.com",
            license="https://creativecommons.org/licenses/by/4.0/",
            version="1.0",
        )
        assert lex["id"] == "test-wn"
        assert lex["label"] == "Test WordNet"
        assert lex["language"] == "en"
        assert lex["entries"] == []
        assert lex["synsets"] == []
        assert lex["meta"] is None
    
    def test_make_lexical_resource(self):
        """Test creating a lexical resource dict."""
        lex = make_lexicon(
            id="test-wn",
            label="Test WordNet",
            language="en",
            email="test@example.com",
            license="https://creativecommons.org/licenses/by/4.0/",
            version="1.0",
        )
        resource = make_lexical_resource([lex])
        
        assert resource["lmf_version"] == "1.4"
        assert len(resource["lexicons"]) == 1
        assert resource["lexicons"][0]["id"] == "test-wn"


@requires_wn
class TestWordnetEditorCreate:
    """Tests for creating new lexicons with WordnetEditor."""
    
    def test_create_new_editor(self):
        """Test creating a new empty lexicon."""
        from wn_edit import WordnetEditor
        
        editor = WordnetEditor(
            create_new=True,
            lexicon_id="test-wn",
            label="Test WordNet",
        )
        
        assert editor.lexicon["id"] == "test-wn"
        assert editor.lexicon["label"] == "Test WordNet"
        assert len(editor.lexicon["synsets"]) == 0
        assert len(editor.lexicon["entries"]) == 0
    
    def test_create_new_requires_id(self):
        """Test that create_new=True requires lexicon_id."""
        from wn_edit import WordnetEditor
        
        with pytest.raises(ValueError, match="lexicon_id is required"):
            WordnetEditor(create_new=True)
    
    def test_must_specify_something(self):
        """Test that either lexicon_specifier or create_new must be provided."""
        from wn_edit import WordnetEditor
        
        with pytest.raises(ValueError):
            WordnetEditor()


@requires_wn
class TestWordnetEditorSynsets:
    """Tests for synset operations."""
    
    @pytest.fixture
    def editor(self):
        """Create a fresh editor for each test."""
        from wn_edit import WordnetEditor
        return WordnetEditor(
            create_new=True,
            lexicon_id="test-wn",
            label="Test WordNet",
        )
    
    def test_create_synset_basic(self, editor):
        """Test creating a basic synset."""
        synset = editor.create_synset(pos="n", definition="A test concept")
        
        assert synset["partOfSpeech"] == "n"
        assert len(synset["definitions"]) == 1
        assert synset["definitions"][0]["text"] == "A test concept"
        assert editor.get_synset(synset["id"]) is synset
    
    def test_create_synset_with_words(self, editor):
        """Test creating a synset with words."""
        synset = editor.create_synset(
            pos="n",
            definition="A test concept",
            words=["testword", "exampleword"],
        )
        
        # Should have created entries
        assert len(editor.lexicon["entries"]) == 2
        
        # Each entry should have a sense pointing to this synset
        for entry in editor.lexicon["entries"]:
            assert len(entry["senses"]) == 1
            assert entry["senses"][0]["synset"] == synset["id"]
    
    def test_create_synset_with_examples(self, editor):
        """Test creating a synset with examples."""
        synset = editor.create_synset(
            pos="v",
            definition="To do something",
            examples=["I did something.", "She does something."],
        )
        
        assert len(synset["examples"]) == 2
    
    def test_modify_synset(self, editor):
        """Test modifying an existing synset."""
        synset = editor.create_synset(pos="n", definition="Original")
        synset_id = synset["id"]
        
        editor.modify_synset(synset_id, definition="Modified")
        
        assert synset["definitions"][0]["text"] == "Modified"
    
    def test_modify_synset_add_examples(self, editor):
        """Test adding examples to a synset."""
        synset = editor.create_synset(pos="n", definition="Test")
        
        editor.modify_synset(
            synset["id"],
            add_examples=["Example 1", "Example 2"],
        )
        
        assert len(synset["examples"]) == 2
    
    def test_remove_synset(self, editor):
        """Test removing a synset."""
        synset = editor.create_synset(
            pos="n",
            definition="To be removed",
            words=["removeword"],
        )
        synset_id = synset["id"]
        
        # Verify it exists
        assert editor.get_synset(synset_id) is not None
        
        # Remove it
        editor.remove_synset(synset_id)
        
        # Verify it's gone
        assert editor.get_synset(synset_id) is None
        
        # Verify senses were removed
        for entry in editor.lexicon["entries"]:
            for sense in entry.get("senses", []):
                assert sense["synset"] != synset_id
    
    def test_add_synset_relation(self, editor):
        """Test adding a relation between synsets."""
        synset1 = editor.create_synset(pos="n", definition="Animal")
        synset2 = editor.create_synset(pos="n", definition="Dog")
        
        editor.add_synset_relation(synset2["id"], synset1["id"], "hypernym")
        
        assert len(synset2["relations"]) == 1
        assert synset2["relations"][0]["target"] == synset1["id"]
        assert synset2["relations"][0]["relType"] == "hypernym"


@requires_wn
class TestWordnetEditorEntries:
    """Tests for lexical entry operations."""
    
    @pytest.fixture
    def editor(self):
        """Create a fresh editor for each test."""
        from wn_edit import WordnetEditor
        return WordnetEditor(
            create_new=True,
            lexicon_id="test-wn",
            label="Test WordNet",
        )
    
    def test_create_entry(self, editor):
        """Test creating a lexical entry."""
        entry = editor.create_entry("dog", "n")
        
        assert entry["lemma"]["writtenForm"] == "dog"
        assert entry["lemma"]["partOfSpeech"] == "n"
        assert entry["senses"] == []
    
    def test_create_entry_with_forms(self, editor):
        """Test creating an entry with forms."""
        entry = editor.create_entry("run", "v", forms=["ran", "running"])
        
        assert len(entry["forms"]) == 2
    
    def test_find_entries(self, editor):
        """Test finding entries by lemma."""
        editor.create_entry("dog", "n")
        editor.create_entry("dog", "v")  # "to dog" someone
        editor.create_entry("cat", "n")
        
        dogs = editor.find_entries("dog")
        assert len(dogs) == 2
        
        dog_nouns = editor.find_entries("dog", pos="n")
        assert len(dog_nouns) == 1
    
    def test_add_word_to_synset(self, editor):
        """Test adding a word to a synset."""
        synset = editor.create_synset(pos="n", definition="A canine")
        
        entry = editor.add_word_to_synset(synset["id"], "dog")
        
        assert entry["lemma"]["writtenForm"] == "dog"
        assert len(entry["senses"]) == 1
        assert entry["senses"][0]["synset"] == synset["id"]
    
    def test_add_word_to_synset_existing_entry(self, editor):
        """Test adding a synset link to an existing word."""
        entry = editor.create_entry("dog", "n")
        synset1 = editor.create_synset(pos="n", definition="A canine")
        synset2 = editor.create_synset(pos="n", definition="A bad person")
        
        editor.add_word_to_synset(synset1["id"], "dog")
        editor.add_word_to_synset(synset2["id"], "dog")
        
        # Should still be one entry
        assert len(editor.find_entries("dog", "n")) == 1
        
        # But with two senses
        entry = editor.find_entries("dog", "n")[0]
        assert len(entry["senses"]) == 2
    
    def test_remove_entry(self, editor):
        """Test removing an entry."""
        entry = editor.create_entry("dog", "n")
        entry_id = entry["id"]
        
        editor.remove_entry(entry_id)
        
        assert editor.get_entry(entry_id) is None
        assert len(editor.find_entries("dog")) == 0


@requires_wn
class TestWordnetEditorExport:
    """Tests for export functionality."""
    
    @pytest.fixture
    def editor(self):
        """Create an editor with some content."""
        from wn_edit import WordnetEditor
        editor = WordnetEditor(
            create_new=True,
            lexicon_id="test-wn",
            label="Test WordNet",
        )
        
        # Add some content
        animal = editor.create_synset(
            pos="n",
            definition="A living organism",
            words=["animal", "creature"],
        )
        dog = editor.create_synset(
            pos="n",
            definition="A domesticated canine",
            words=["dog", "hound"],
        )
        editor.add_synset_relation(dog["id"], animal["id"], "hypernym")
        
        return editor
    
    def test_export_creates_file(self, editor, tmp_path):
        """Test that export creates a file."""
        output_file = tmp_path / "test.xml"
        
        editor.export(output_file)
        
        assert output_file.exists()
        assert output_file.stat().st_size > 0
    
    def test_export_valid_xml(self, editor, tmp_path):
        """Test that exported file is valid XML."""
        import xml.etree.ElementTree as ET
        
        output_file = tmp_path / "test.xml"
        editor.export(output_file)
        
        # Should parse without error
        tree = ET.parse(output_file)
        root = tree.getroot()
        
        assert root.tag == "LexicalResource"
    
    def test_export_can_be_loaded(self, editor, tmp_path):
        """Test that exported file can be loaded by wn.lmf.load()."""
        from wn import lmf
        
        output_file = tmp_path / "test.xml"
        editor.export(output_file)
        
        # Should load without error
        resource = lmf.load(output_file)
        
        assert resource["lmf_version"] == "1.4"
        assert len(resource["lexicons"]) == 1
        assert resource["lexicons"][0]["id"] == "test-wn"


@requires_wn
class TestWordnetEditorStats:
    """Tests for statistics methods."""
    
    def test_stats(self):
        """Test getting statistics."""
        from wn_edit import WordnetEditor
        
        editor = WordnetEditor(
            create_new=True,
            lexicon_id="test-wn",
            label="Test WordNet",
        )
        
        # Empty initially
        stats = editor.stats()
        assert stats["synsets"] == 0
        assert stats["entries"] == 0
        assert stats["senses"] == 0
        
        # Add content
        editor.create_synset(
            pos="n",
            definition="Test",
            words=["word1", "word2"],
        )
        
        stats = editor.stats()
        assert stats["synsets"] == 1
        assert stats["entries"] == 2
        assert stats["senses"] == 2


@requires_wn
class TestWordnetEditorMetadata:
    """Tests for lexicon metadata operations."""
    
    @pytest.fixture
    def editor(self):
        """Create a fresh editor for each test."""
        from wn_edit import WordnetEditor
        return WordnetEditor(
            create_new=True,
            lexicon_id="test-wn",
            label="Test WordNet",
            version="1.0",
            email="original@example.com",
            license="https://example.com/license",
        )
    
    def test_get_metadata(self, editor):
        """Test getting metadata."""
        meta = editor.get_metadata()
        
        assert meta["id"] == "test-wn"
        assert meta["label"] == "Test WordNet"
        assert meta["version"] == "1.0"
        assert meta["email"] == "original@example.com"
    
    def test_set_version(self, editor):
        """Test setting version."""
        editor.set_version("2.0")
        assert editor.lexicon["version"] == "2.0"
        assert editor.get_metadata()["version"] == "2.0"
    
    def test_set_label(self, editor):
        """Test setting label."""
        editor.set_label("Updated WordNet")
        assert editor.lexicon["label"] == "Updated WordNet"
    
    def test_update_metadata(self, editor):
        """Test updating multiple metadata fields."""
        editor.update_metadata(
            version="1.1",
            label="Test WordNet (Extended)",
            email="new@example.com",
            url="https://example.com/wordnet",
            citation="Cite this as...",
        )
        
        meta = editor.get_metadata()
        assert meta["version"] == "1.1"
        assert meta["label"] == "Test WordNet (Extended)"
        assert meta["email"] == "new@example.com"
        assert meta["url"] == "https://example.com/wordnet"
        assert meta["citation"] == "Cite this as..."
        # License should be unchanged
        assert meta["license"] == "https://example.com/license"
    
    def test_metadata_persists_in_export(self, editor, tmp_path):
        """Test that metadata changes are preserved in export."""
        from wn import lmf
        
        editor.update_metadata(
            version="2.0",
            label="Exported WordNet",
        )
        
        output_file = tmp_path / "test.xml"
        editor.export(output_file)
        
        # Load and verify
        resource = lmf.load(output_file)
        lexicon = resource["lexicons"][0]
        
        assert lexicon["version"] == "2.0"
        assert lexicon["label"] == "Exported WordNet"


@requires_wn
class TestWordnetEditorMetadataOverride:
    """Tests for metadata override when loading existing lexicons."""
    
    @pytest.fixture
    def source_xml(self, tmp_path):
        """Create a source XML file to load from."""
        from wn_edit import WordnetEditor
        
        editor = WordnetEditor(
            create_new=True,
            lexicon_id="source-wn",
            label="Source WordNet",
            version="1.0",
            email="source@example.com",
            license="https://example.com/license",
        )
        
        # Add some content
        editor.create_synset(
            pos="n",
            definition="A test concept",
            words=["testword"],
        )
        
        output_file = tmp_path / "source.xml"
        editor.export(output_file)
        return output_file
    
    def test_override_lexicon_id_on_load(self, source_xml):
        """Test that lexicon_id can be overridden when loading."""
        from wn_edit import WordnetEditor
        
        editor = WordnetEditor.load_from_file(source_xml)
        
        # Original ID
        assert editor.lexicon["id"] == "source-wn"
        
        # Now load with override - need to use set_id after loading
        editor2 = WordnetEditor.load_from_file(source_xml)
        editor2.set_id("derived-wn")
        
        assert editor2.lexicon["id"] == "derived-wn"
        # Other metadata should be unchanged
        assert editor2.lexicon["label"] == "Source WordNet"
        assert editor2.lexicon["version"] == "1.0"
    
    def test_override_version_on_load(self, source_xml):
        """Test that version can be overridden when loading."""
        from wn_edit import WordnetEditor
        
        editor = WordnetEditor.load_from_file(source_xml)
        editor.set_version("2.0-derived")
        
        assert editor.lexicon["version"] == "2.0-derived"
        # Other metadata should be unchanged
        assert editor.lexicon["id"] == "source-wn"
        assert editor.lexicon["label"] == "Source WordNet"
    
    def test_override_label_on_load(self, source_xml):
        """Test that label can be overridden when loading."""
        from wn_edit import WordnetEditor
        
        editor = WordnetEditor.load_from_file(source_xml)
        editor.set_label("Derived WordNet with Extensions")
        
        assert editor.lexicon["label"] == "Derived WordNet with Extensions"
    
    def test_override_multiple_metadata_on_load(self, source_xml):
        """Test overriding multiple metadata fields when loading."""
        from wn_edit import WordnetEditor
        
        editor = WordnetEditor.load_from_file(source_xml)
        editor.set_id("derived-wn")
        editor.set_version("2.0")
        editor.set_label("Derived WordNet")
        
        assert editor.lexicon["id"] == "derived-wn"
        assert editor.lexicon["version"] == "2.0"
        assert editor.lexicon["label"] == "Derived WordNet"
        # Content should be preserved
        assert editor.stats()["synsets"] == 1
        assert editor.stats()["entries"] == 1
    
    def test_override_metadata_persists_in_export(self, source_xml, tmp_path):
        """Test that overridden metadata is preserved when exporting."""
        from wn_edit import WordnetEditor
        from wn import lmf
        
        editor = WordnetEditor.load_from_file(source_xml)
        editor.set_id("derived-wn")
        editor.set_version("2.0")
        editor.set_label("Derived WordNet")
        
        output_file = tmp_path / "derived.xml"
        editor.export(output_file)
        
        # Load and verify
        resource = lmf.load(output_file)
        lexicon = resource["lexicons"][0]
        
        assert lexicon["id"] == "derived-wn"
        assert lexicon["version"] == "2.0"
        assert lexicon["label"] == "Derived WordNet"
        # Content should be preserved
        assert len(lexicon["synsets"]) == 1
        assert len(lexicon["entries"]) == 1
    
    def test_set_id_method(self):
        """Test the set_id method works correctly."""
        from wn_edit import WordnetEditor
        
        editor = WordnetEditor(
            create_new=True,
            lexicon_id="original-id",
            label="Test WordNet",
        )
        
        assert editor.lexicon["id"] == "original-id"
        
        editor.set_id("new-id")
        
        assert editor.lexicon["id"] == "new-id"
    
    def test_lmf_version_can_be_set(self, source_xml, tmp_path):
        """Test that lmf_version can be controlled."""
        from wn_edit import WordnetEditor
        from wn import lmf
        
        editor = WordnetEditor.load_from_file(source_xml)
        # The resource's lmf_version should be accessible
        assert "lmf_version" in editor.resource
        
        # Modify it
        editor.resource["lmf_version"] = "1.4"
        
        output_file = tmp_path / "output.xml"
        editor.export(output_file)
        
        # Verify in exported file
        resource = lmf.load(output_file)
        assert resource["lmf_version"] == "1.4"


@requires_wn  
class TestWordnetEditorInitOverride:
    """Tests for metadata override via __init__ parameters when loading from database.
    
    These tests verify that when loading an existing lexicon with lexicon_specifier,
    the lexicon_id, label, version, and lmf_version parameters can override the
    values from the loaded lexicon. This is useful for creating derivative works.
    """
    
    @pytest.fixture
    def installed_lexicon(self):
        """Create and install a test lexicon in the wn database."""
        import wn
        from wn_edit import WordnetEditor
        
        # Create a unique lexicon ID to avoid conflicts
        import uuid
        unique_id = f"test-override-{uuid.uuid4().hex[:8]}"
        
        editor = WordnetEditor(
            create_new=True,
            lexicon_id=unique_id,
            label="Original Label",
            version="1.0",
            email="test@example.com",
            license="https://example.com/license",
        )
        
        # Add some content
        editor.create_synset(
            pos="n",
            definition="A test concept",
            words=["testword"],
        )
        
        # Commit to database (this uses wn.add_lexical_resource internally)
        editor.commit()
        
        yield unique_id, "1.0"
        
        # Cleanup: remove from database
        try:
            wn.remove(f'{unique_id}:*')
        except Exception:
            pass
    
    def test_override_metadata_via_init_params(self, installed_lexicon, tmp_path):
        """Test that metadata can be overridden via __init__ parameters."""
        from wn_edit import WordnetEditor
        from wn import lmf
        
        lex_id, version = installed_lexicon
        specifier = f"{lex_id}:{version}"
        
        # Load with overrides
        editor = WordnetEditor(
            specifier,
            lexicon_id=f"{lex_id}-derived",
            label="Derived Label",
            version="2.0",
            lmf_version="1.4",
        )
        
        # Verify overrides were applied
        assert editor.lexicon["id"] == f"{lex_id}-derived"
        assert editor.lexicon["label"] == "Derived Label"
        assert editor.lexicon["version"] == "2.0"
        assert editor.resource["lmf_version"] == "1.4"
        
        # Content should be preserved
        assert editor.stats()["synsets"] == 1
        assert editor.stats()["entries"] == 1
        
        # Export and verify
        output_file = tmp_path / "derived.xml"
        editor.export(output_file)
        
        resource = lmf.load(output_file)
        lexicon = resource["lexicons"][0]
        
        assert lexicon["id"] == f"{lex_id}-derived"
        assert lexicon["label"] == "Derived Label"
        assert lexicon["version"] == "2.0"
        assert resource["lmf_version"] == "1.4"
    
    def test_partial_override_via_init_params(self, installed_lexicon):
        """Test that only specified parameters are overridden."""
        from wn_edit import WordnetEditor
        
        lex_id, version = installed_lexicon
        specifier = f"{lex_id}:{version}"
        
        # Load with only label override
        editor = WordnetEditor(
            specifier,
            label="New Label Only",
        )
        
        # Label should be overridden
        assert editor.lexicon["label"] == "New Label Only"
        # ID and version should be unchanged
        assert editor.lexicon["id"] == lex_id
        # Note: version default is "1.0" so it won't override unless different
    
    def test_no_override_when_no_params(self, installed_lexicon):
        """Test that no override happens when no params are provided."""
        from wn_edit import WordnetEditor
        
        lex_id, version = installed_lexicon
        specifier = f"{lex_id}:{version}"
        
        # Load without overrides
        editor = WordnetEditor(specifier)
        
        # All original values should be preserved
        assert editor.lexicon["id"] == lex_id
        assert editor.lexicon["label"] == "Original Label"
        assert editor.lexicon["version"] == "1.0"
    """Integration tests for creating, exporting, loading, modifying, and re-exporting."""
    
    def test_create_dump_load_modify_dump(self, tmp_path):
        """Test full round-trip: create -> dump -> load -> modify -> dump."""
        from wn_edit import WordnetEditor
        from wn import lmf
        import xml.etree.ElementTree as ET
        
        # Step 1: Create a new wordnet from scratch
        editor = WordnetEditor(
            create_new=True,
            lexicon_id="my-wordnet",
            label="My Test WordNet",
            language="en",
            email="test@example.com",
            license="https://creativecommons.org/licenses/by/4.0/",
            version="1.0",
        )
        
        # Add some content
        animal = editor.create_synset(
            pos="n",
            definition="A living organism that feeds on organic matter",
            words=["animal", "creature", "beast"],
            examples=["Animals need food and water to survive."],
        )
        
        dog = editor.create_synset(
            pos="n",
            definition="A domesticated carnivorous mammal",
            words=["dog", "canine", "hound"],
            examples=["The dog barked at the mailman."],
        )
        
        cat = editor.create_synset(
            pos="n",
            definition="A small domesticated feline",
            words=["cat", "feline", "kitty"],
        )
        
        # Add relations
        editor.add_synset_relation(dog["id"], animal["id"], "hypernym")
        editor.add_synset_relation(cat["id"], animal["id"], "hypernym")
        
        # Verify initial state
        stats = editor.stats()
        assert stats["synsets"] == 3
        assert stats["entries"] == 9  # 3 + 3 + 3 words
        
        # Step 2: Export to file
        first_export = tmp_path / "my_wordnet_v1.xml"
        editor.export(first_export)
        
        assert first_export.exists()
        assert first_export.stat().st_size > 0
        
        # Step 2b: Verify XML structure
        tree = ET.parse(first_export)
        root = tree.getroot()
        
        assert root.tag == "LexicalResource"
        
        lexicon_elem = root.find("Lexicon")
        assert lexicon_elem is not None
        assert lexicon_elem.get("id") == "my-wordnet"
        assert lexicon_elem.get("label") == "My Test WordNet"
        assert lexicon_elem.get("language") == "en"
        assert lexicon_elem.get("version") == "1.0"
        
        # Check synsets in XML
        synset_elems = lexicon_elem.findall("Synset")
        assert len(synset_elems) == 3
        
        # Check entries in XML
        entry_elems = lexicon_elem.findall("LexicalEntry")
        assert len(entry_elems) == 9
        
        # Verify a specific entry structure
        dog_entry = None
        for entry in entry_elems:
            lemma = entry.find("Lemma")
            if lemma is not None and lemma.get("writtenForm") == "dog":
                dog_entry = entry
                break
        
        assert dog_entry is not None
        assert dog_entry.find("Lemma").get("partOfSpeech") == "n"
        assert dog_entry.find("Sense") is not None
        
        # Step 3: Load the exported file back
        resource = lmf.load(first_export)
        
        assert resource["lmf_version"] == "1.4"
        assert len(resource["lexicons"]) == 1
        assert resource["lexicons"][0]["id"] == "my-wordnet"
        assert resource["lexicons"][0]["label"] == "My Test WordNet"
        assert len(resource["lexicons"][0]["synsets"]) == 3
        assert len(resource["lexicons"][0]["entries"]) == 9
        
        # Step 4: Load using class method and modify
        editor2 = WordnetEditor.load_from_file(first_export)
        
        # Verify loaded state
        stats2 = editor2.stats()
        assert stats2["synsets"] == 3
        assert stats2["entries"] == 9
        
        # Step 5: Modify the loaded wordnet
        # Update version
        editor2.update_metadata(version="1.1", label="My Test WordNet (Extended)")
        
        # Add a new synset
        bird = editor2.create_synset(
            pos="n",
            definition="A warm-blooded egg-laying vertebrate with feathers and wings",
            words=["bird", "avian"],
        )
        editor2.add_synset_relation(bird["id"], animal["id"], "hypernym")
        
        # Add a word to an existing synset (need to find dog synset in loaded data)
        dog_synset_id = None
        for synset in editor2.lexicon["synsets"]:
            defs = synset.get("definitions", [])
            if defs and "carnivorous" in defs[0].get("text", ""):
                dog_synset_id = synset["id"]
                break
        
        assert dog_synset_id is not None
        editor2.add_word_to_synset(dog_synset_id, "pooch")
        
        # Verify modified state
        stats3 = editor2.stats()
        assert stats3["synsets"] == 4  # Added bird
        assert stats3["entries"] == 12  # Added bird(2) + pooch(1)
        
        # Step 6: Export the modified wordnet
        second_export = tmp_path / "my_wordnet_v2.xml"
        editor2.export(second_export)
        
        assert second_export.exists()
        
        # Step 6b: Verify modified XML structure
        tree2 = ET.parse(second_export)
        root2 = tree2.getroot()
        
        lexicon_elem2 = root2.find("Lexicon")
        assert lexicon_elem2.get("version") == "1.1"
        assert lexicon_elem2.get("label") == "My Test WordNet (Extended)"
        
        synset_elems2 = lexicon_elem2.findall("Synset")
        assert len(synset_elems2) == 4
        
        entry_elems2 = lexicon_elem2.findall("LexicalEntry")
        assert len(entry_elems2) == 12
        
        # Verify pooch was added
        pooch_entry = None
        for entry in entry_elems2:
            lemma = entry.find("Lemma")
            if lemma is not None and lemma.get("writtenForm") == "pooch":
                pooch_entry = entry
                break
        
        assert pooch_entry is not None
        
        # Step 7: Load and verify the modified version
        resource2 = lmf.load(second_export)
        
        assert len(resource2["lexicons"][0]["synsets"]) == 4
        assert len(resource2["lexicons"][0]["entries"]) == 12
        assert resource2["lexicons"][0]["version"] == "1.1"
    
    def test_load_from_file_classmethod(self, tmp_path):
        """Test the load_from_file class method for clean round-trip editing."""
        from wn_edit import WordnetEditor
        from wn import lmf
        
        # Step 1: Create a new wordnet
        editor = WordnetEditor(
            create_new=True,
            lexicon_id="round-trip-test",
            label="Round Trip Test",
            language="en",
            email="test@example.com",
            license="https://creativecommons.org/licenses/by/4.0/",
            version="1.0",
        )
        
        # Add content
        editor.create_synset(
            pos="n",
            definition="A four-legged animal",
            words=["dog", "hound"],
        )
        
        # Export
        xml_v1 = tmp_path / "wordnet_v1.xml"
        editor.export(xml_v1)
        
        # Step 2: Load from file using class method
        editor2 = WordnetEditor.load_from_file(xml_v1)
        
        # Verify loaded correctly
        assert editor2.lexicon["id"] == "round-trip-test"
        assert editor2.lexicon["label"] == "Round Trip Test"
        assert editor2.stats()["synsets"] == 1
        assert editor2.stats()["entries"] == 2
        
        # Step 3: Modify
        editor2.set_version("1.1")
        editor2.create_synset(
            pos="n",
            definition="A feline animal",
            words=["cat", "kitty"],
        )
        
        # Step 4: Export modified version
        xml_v2 = tmp_path / "wordnet_v2.xml"
        editor2.export(xml_v2)
        
        # Step 5: Verify final result
        editor3 = WordnetEditor.load_from_file(xml_v2)
        assert editor3.stats()["synsets"] == 2
        assert editor3.stats()["entries"] == 4
        assert editor3.get_metadata()["version"] == "1.1"
        
        # Verify we can find the entries
        dogs = editor3.find_entries("dog")
        cats = editor3.find_entries("cat")
        assert len(dogs) == 1
        assert len(cats) == 1
