"""Integration tests for wn_edit with the wn library.

These tests verify that:
1. After commit(), synsets are queryable via standard wn functions
2. Relations work (hypernym_paths, etc.)
3. ILI identifiers are preserved
4. Lemmas and words are accessible

Note: These tests require the wn package. Test lexicons are automatically
cleaned up after each test.
"""

import pytest
import uuid

# Check if wn is available
try:
    import wn
    HAS_WN = True
except ImportError:
    HAS_WN = False

pytestmark = pytest.mark.skipif(not HAS_WN, reason="wn package not installed")

# Track lexicons created during tests for cleanup
_created_lexicons: list[str] = []


def unique_lexicon_id(prefix: str = "test") -> str:
    """Generate a unique lexicon ID for testing and track it for cleanup."""
    lex_id = f"{prefix}-{uuid.uuid4().hex[:8]}"
    _created_lexicons.append(lex_id)
    return lex_id


@pytest.fixture(autouse=True)
def cleanup_test_lexicons():
    """Automatically clean up any test lexicons after each test."""
    # Clear the list before test
    _created_lexicons.clear()
    
    yield  # Run the test
    
    # Clean up after test
    for lex_id in _created_lexicons:
        try:
            # Use wildcard to match any version
            wn.remove(f'{lex_id}:*')
        except Exception:
            # Ignore errors if lexicon doesn't exist or can't be removed
            pass
    
    _created_lexicons.clear()


class TestWnIntegration:
    """Test that committed changes are queryable via wn."""
    
    def test_commit_and_query_synset(self):
        """Test that a committed synset can be queried via wn.synsets()."""
        from wn_edit import WordnetEditor
        
        lex_id = unique_lexicon_id("integration")
        
        # Create a new wordnet
        editor = WordnetEditor(
            create_new=True,
            lexicon_id=lex_id,
            label='Test Integration WordNet',
            language='en',
            email='test@example.com',
            license='https://creativecommons.org/licenses/by/4.0/',
            version='1.0',
        )
        
        # Add a synset with a word
        editor.create_synset(
            pos='n',
            definition='A test animal for integration testing',
            words=['testanimal'],
        )
        
        # Commit to database
        editor.commit()
        
        # Query via wn using our specific lexicon
        my_wn = wn.Wordnet(lex_id)
        synsets = my_wn.synsets('testanimal')
        assert len(synsets) >= 1
        
        # Check the definition
        ss = synsets[0]
        assert ss.definition() == 'A test animal for integration testing'
    
    def test_commit_and_query_lemmas(self):
        """Test that lemmas are accessible after commit."""
        from wn_edit import WordnetEditor
        
        lex_id = unique_lexicon_id("lemmas")
        
        editor = WordnetEditor(
            create_new=True,
            lexicon_id=lex_id,
            label='Test Lemmas',
            language='en',
            email='test@example.com',
            license='https://creativecommons.org/licenses/by/4.0/',
            version='1.0',
        )
        
        # Add a synset with multiple words
        editor.create_synset(
            pos='n',
            definition='A furry pet for testing',
            words=['testcat', 'testkitty', 'testfeline'],
        )
        
        editor.commit()
        
        # Query and check lemmas
        my_wn = wn.Wordnet(lex_id)
        synsets = my_wn.synsets('testcat')
        assert len(synsets) >= 1
        
        ss = synsets[0]
        lemmas = ss.lemmas()
        assert 'testcat' in lemmas
        assert 'testkitty' in lemmas
        assert 'testfeline' in lemmas
    
    def test_commit_with_relations(self):
        """Test that relations are queryable after commit."""
        from wn_edit import WordnetEditor
        
        lex_id = unique_lexicon_id("relations")
        
        editor = WordnetEditor(
            create_new=True,
            lexicon_id=lex_id,
            label='Test Relations',
            language='en',
            email='test@example.com',
            license='https://creativecommons.org/licenses/by/4.0/',
            version='1.0',
        )
        
        # Create animal (hypernym)
        animal = editor.create_synset(
            pos='n',
            definition='A living organism for testing',
            words=['testorganism'],
        )
        
        # Create dog (hyponym of animal)
        dog = editor.create_synset(
            pos='n',
            definition='A domesticated canine for testing',
            words=['testcanine'],
        )
        
        # Create poodle (hyponym of dog)
        poodle = editor.create_synset(
            pos='n',
            definition='A breed of dog with curly hair for testing',
            words=['testpoodle'],
        )
        
        # Add hypernym relations
        editor.add_synset_relation(dog['id'], animal['id'], 'hypernym')
        editor.add_synset_relation(poodle['id'], dog['id'], 'hypernym')
        
        editor.commit()
        
        # Query poodle and check hypernym path
        my_wn = wn.Wordnet(lex_id)
        poodle_synsets = my_wn.synsets('testpoodle')
        assert len(poodle_synsets) >= 1
        
        poodle_ss = poodle_synsets[0]
        
        # Get hypernyms
        hypernyms = poodle_ss.hypernyms()
        assert len(hypernyms) >= 1
        assert 'testcanine' in hypernyms[0].lemmas()
        
        # Check hypernym paths
        paths = poodle_ss.hypernym_paths()
        assert len(paths) >= 1
        
        # The path should go poodle -> dog -> animal
        path_lemmas = [ss.lemmas() for ss in paths[0]]
        # Flatten and check
        all_lemmas = [lemma for lemmas in path_lemmas for lemma in lemmas]
        assert 'testcanine' in all_lemmas
        assert 'testorganism' in all_lemmas
    
    def test_commit_with_ili(self):
        """Test that ILI identifiers are preserved after commit."""
        from wn_edit import WordnetEditor
        
        lex_id = unique_lexicon_id("ili")
        
        editor = WordnetEditor(
            create_new=True,
            lexicon_id=lex_id,
            label='Test ILI',
            language='en',
            email='test@example.com',
            license='https://creativecommons.org/licenses/by/4.0/',
            version='1.0',
        )
        
        # Create a synset with an ILI
        # Use a test ILI - i99999999 (unlikely to conflict)
        editor.create_synset(
            pos='n',
            definition='A domesticated carnivorous mammal for testing',
            words=['testilidog'],
            ili='i99999999',
        )
        
        editor.commit()
        
        # Query and check ILI
        my_wn = wn.Wordnet(lex_id)
        synsets = my_wn.synsets('testilidog')
        assert len(synsets) >= 1
        
        ss = synsets[0]
        
        # Check the ILI is accessible (ili is a property, not a method)
        ili = ss.ili
        assert ili is not None
        assert ili.id == 'i99999999'
    
    def test_commit_with_examples(self):
        """Test that examples are preserved after commit."""
        from wn_edit import WordnetEditor
        
        lex_id = unique_lexicon_id("examples")
        
        editor = WordnetEditor(
            create_new=True,
            lexicon_id=lex_id,
            label='Test Examples',
            language='en',
            email='test@example.com',
            license='https://creativecommons.org/licenses/by/4.0/',
            version='1.0',
        )
        
        editor.create_synset(
            pos='n',
            definition='A domesticated canine for testing examples',
            words=['testexampledog'],
            examples=[
                'The testexampledog barked at the mailman.',
                'She walked her testexampledog in the park.',
            ],
        )
        
        editor.commit()
        
        my_wn = wn.Wordnet(lex_id)
        synsets = my_wn.synsets('testexampledog')
        assert len(synsets) >= 1
        
        ss = synsets[0]
        examples = ss.examples()
        assert len(examples) == 2
        assert 'The testexampledog barked at the mailman.' in examples
        assert 'She walked her testexampledog in the park.' in examples
    
    def test_query_by_lexicon(self):
        """Test querying specifically by lexicon ID."""
        from wn_edit import WordnetEditor
        
        lex_id = unique_lexicon_id("custom")
        
        editor = WordnetEditor(
            create_new=True,
            lexicon_id=lex_id,
            label='My Custom WordNet',
            language='en',
            email='test@example.com',
            license='https://creativecommons.org/licenses/by/4.0/',
            version='1.0',
        )
        
        editor.create_synset(
            pos='n',
            definition='A unique test concept',
            words=['uniquetestword'],
        )
        
        editor.commit()
        
        # Query by lexicon
        my_wn = wn.Wordnet(lex_id)
        synsets = my_wn.synsets('uniquetestword')
        assert len(synsets) == 1
        assert synsets[0].definition() == 'A unique test concept'
    
    def test_words_function(self):
        """Test that wn.words() works for committed entries."""
        from wn_edit import WordnetEditor
        
        lex_id = unique_lexicon_id("words")
        
        editor = WordnetEditor(
            create_new=True,
            lexicon_id=lex_id,
            label='Test Words',
            language='en',
            email='test@example.com',
            license='https://creativecommons.org/licenses/by/4.0/',
            version='1.0',
        )
        
        editor.create_synset(
            pos='n',
            definition='A test concept for words function',
            words=['testword123unique'],
        )
        
        editor.commit()
        
        # Query using wn.Wordnet().words()
        my_wn = wn.Wordnet(lex_id)
        words = my_wn.words('testword123unique')
        assert len(words) >= 1
        
        word = words[0]
        assert word.lemma() == 'testword123unique'
        
        # Check senses
        senses = word.senses()
        assert len(senses) >= 1
    
    def test_senses_function(self):
        """Test that wn.senses() works for committed data."""
        from wn_edit import WordnetEditor
        
        lex_id = unique_lexicon_id("senses")
        
        editor = WordnetEditor(
            create_new=True,
            lexicon_id=lex_id,
            label='Test Senses',
            language='en',
            email='test@example.com',
            license='https://creativecommons.org/licenses/by/4.0/',
            version='1.0',
        )
        
        editor.create_synset(
            pos='n',
            definition='First meaning of testmulti',
            words=['testmultisense'],
        )
        
        editor.create_synset(
            pos='n',
            definition='Second meaning of testmulti',
            words=['testmultisense'],
        )
        
        editor.commit()
        
        # Query senses
        my_wn = wn.Wordnet(lex_id)
        senses = my_wn.senses('testmultisense')
        assert len(senses) >= 2
        
        # Check we have both definitions
        definitions = {s.synset().definition() for s in senses}
        assert 'First meaning of testmulti' in definitions
        assert 'Second meaning of testmulti' in definitions


class TestILIIntegration:
    """Test ILI (Interlingual Index) functionality."""
    
    def test_ili_format(self):
        """Test that ILI is stored in correct format."""
        from wn_edit import WordnetEditor
        
        lex_id = unique_lexicon_id("ili-format")
        
        editor = WordnetEditor(
            create_new=True,
            lexicon_id=lex_id,
            label='Test ILI Format',
            language='en',
            email='test@example.com',
            license='https://creativecommons.org/licenses/by/4.0/',
            version='1.0',
        )
        
        # Test with 'i' prefix
        synset = editor.create_synset(
            pos='n',
            definition='Test with i prefix',
            words=['testili1unique'],
            ili='i12345678',
        )
        
        assert synset['ili'] == 'i12345678'
        
        editor.commit()
        
        my_wn = wn.Wordnet(lex_id)
        ss = my_wn.synsets('testili1unique')[0]
        # ili is a property, not a method
        assert ss.ili.id == 'i12345678'
    
    def test_empty_ili(self):
        """Test synset without ILI."""
        from wn_edit import WordnetEditor
        
        lex_id = unique_lexicon_id("no-ili")
        
        editor = WordnetEditor(
            create_new=True,
            lexicon_id=lex_id,
            label='Test No ILI',
            language='en',
            email='test@example.com',
            license='https://creativecommons.org/licenses/by/4.0/',
            version='1.0',
        )
        
        # Create without ILI
        synset = editor.create_synset(
            pos='n',
            definition='Test without ILI',
            words=['testnoiliunique'],
        )
        
        # Should have empty string (required by wn.lmf.dump)
        assert synset['ili'] == ''
        
        editor.commit()
        
        my_wn = wn.Wordnet(lex_id)
        ss = my_wn.synsets('testnoiliunique')[0]
        # ILI should be None when not set (ili is a property, not a method)
        ili = ss.ili
        assert ili is None


class TestRoundTripWithWn:
    """Test round-trip: create -> commit -> query -> export."""
    
    def test_full_round_trip(self):
        """Test complete workflow with wn integration."""
        from wn_edit import WordnetEditor
        import tempfile
        import os
        
        lex_id = unique_lexicon_id("roundtrip")
        
        # Step 1: Create and populate
        editor = WordnetEditor(
            create_new=True,
            lexicon_id=lex_id,
            label='Round Trip Test',
            language='en',
            email='test@example.com',
            license='https://creativecommons.org/licenses/by/4.0/',
            version='1.0',
        )
        
        animal = editor.create_synset(
            pos='n',
            definition='A living creature for roundtrip',
            words=['roundtripanimal', 'roundtripcreature'],
            ili='i88888888',
        )
        
        dog = editor.create_synset(
            pos='n',
            definition='A pet canine for roundtrip',
            words=['roundtripdog', 'roundtriphphound'],
            ili='i88888889',
        )
        
        editor.add_synset_relation(dog['id'], animal['id'], 'hypernym')
        
        # Step 2: Commit
        editor.commit()
        
        # Step 3: Query via wn
        my_wn = wn.Wordnet(lex_id)
        
        dog_synsets = my_wn.synsets('roundtripdog')
        assert len(dog_synsets) == 1
        
        dog_ss = dog_synsets[0]
        assert dog_ss.definition() == 'A pet canine for roundtrip'
        assert 'roundtripdog' in dog_ss.lemmas()
        assert 'roundtriphphound' in dog_ss.lemmas()
        
        # Check hypernym
        hypernyms = dog_ss.hypernyms()
        assert len(hypernyms) == 1
        assert 'roundtripanimal' in hypernyms[0].lemmas()
        
        # Step 4: Export the queried wordnet
        # wn.export() takes lexicons, not a Wordnet object
        with tempfile.NamedTemporaryFile(suffix='.xml', delete=False) as f:
            export_path = f.name
        
        try:
            # Get the lexicons from the Wordnet object
            lexicons = my_wn.lexicons()
            wn.export(lexicons, export_path)
            
            # Verify export exists and has content
            assert os.path.exists(export_path)
            assert os.path.getsize(export_path) > 0
        finally:
            os.unlink(export_path)
