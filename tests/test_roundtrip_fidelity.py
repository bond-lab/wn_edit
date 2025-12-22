"""Round-trip fidelity tests for wn_edit.

These tests verify that loading a wordnet, making minimal changes, and
exporting preserves all original data except for the intended changes.

These tests are SLOW and require large wordnets to be installed.
They are skipped by default (via pyproject.toml: addopts = "-m 'not slow'").
OEWN will be automatically downloaded if not already installed.

To run these tests:
    hatch test -- -m slow

Or to run ALL tests including slow ones:
    hatch test -- -m ''
"""

import pytest
import tempfile
from pathlib import Path

# Check if wn is available
try:
    import wn
    HAS_WN = True
except ImportError:
    HAS_WN = False


# Skip all tests in this module if wn is not available
pytestmark = [
    pytest.mark.skipif(not HAS_WN, reason="wn package not installed"),
    pytest.mark.slow,
]


def normalize_xml_for_comparison(xml_path: Path) -> list[str]:
    """Read and normalize XML for comparison.
    
    Returns a list of lines with consistent formatting.
    Normalizes trailing whitespace in text content which may be
    stripped by the wn.lmf load/dump cycle.
    """
    import re
    
    with open(xml_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    normalized = []
    for line in lines:
        # Strip trailing whitespace from the line itself
        line = line.rstrip()
        # Also normalize trailing whitespace before closing tags
        # e.g., "Public interests </Example>" -> "Public interests</Example>"
        line = re.sub(r'\s+(</(Example|Definition|ILIDefinition)>)', r'\1', line)
        normalized.append(line)
    
    return normalized


def find_xml_differences(original_lines: list[str], modified_lines: list[str]) -> list[tuple[int, str, str]]:
    """Find differences between two XML files.
    
    Returns list of (line_number, original_line, modified_line) tuples.
    """
    differences = []
    max_lines = max(len(original_lines), len(modified_lines))
    
    for i in range(max_lines):
        orig = original_lines[i] if i < len(original_lines) else "<missing>"
        mod = modified_lines[i] if i < len(modified_lines) else "<missing>"
        
        if orig != mod:
            differences.append((i + 1, orig, mod))
    
    return differences


class TestRoundTripFidelity:
    """Test that round-trip editing preserves data fidelity."""
    
    @pytest.fixture
    def oewn_lexicon(self):
        """Get the OEWN lexicon, downloading if necessary."""
        # Try to download OEWN if not present (skips if already installed)
        try:
            wn.download('oewn:2024')
        except Exception as e:
            # May fail if already installed with different version, that's ok
            print(f"Download note: {e}")
        
        # Try to find OEWN
        lexicons = wn.lexicons()
        for lex in lexicons:
            lex_id = lex.id
            if lex_id.startswith('oewn') or lex_id.startswith('ewn'):
                return lex
        
        # If no OEWN, list what we have
        if lexicons:
            pytest.skip(f"No OEWN found. Available lexicons: {[l.id for l in lexicons]}")
        else:
            pytest.skip("No lexicons installed. Run: python -c \"import wn; wn.download('oewn:2024')\"")
    
    def test_version_change_only(self, oewn_lexicon):
        """Test that changing only the version produces minimal XML diff."""
        from wn_edit import WordnetEditor
        
        lex_id = oewn_lexicon.id
        original_version = oewn_lexicon.version
        new_version = original_version + "-test"
        
        with tempfile.TemporaryDirectory() as tmpdir:
            original_path = Path(tmpdir) / "original.xml"
            modified_path = Path(tmpdir) / "modified.xml"
            
            # Export the original
            wn.export([oewn_lexicon], original_path)
            
            # Load into editor and change version
            editor = WordnetEditor(f"{lex_id}:{original_version}")
            editor.set_version(new_version)
            
            # Export the modified version
            editor.export(modified_path)
            
            # Compare the XML files
            original_lines = normalize_xml_for_comparison(original_path)
            modified_lines = normalize_xml_for_comparison(modified_path)
            
            differences = find_xml_differences(original_lines, modified_lines)
            
            # Should have exactly 1 difference: the version attribute
            assert len(differences) > 0, "Expected at least one difference (version change)"
            
            # Check that all differences are version-related
            for line_num, orig, mod in differences:
                # The difference should be in the version attribute
                assert 'version=' in orig or 'version=' in mod, (
                    f"Unexpected difference at line {line_num}:\n"
                    f"  Original: {orig}\n"
                    f"  Modified: {mod}"
                )
                # Verify it's the expected version change
                if 'version=' in orig and 'version=' in mod:
                    assert original_version in orig, f"Original version not found in: {orig}"
                    assert new_version in mod, f"New version not found in: {mod}"
            
            print(f"\n✓ Round-trip test passed!")
            print(f"  Lexicon: {lex_id}:{original_version}")
            print(f"  Original file size: {original_path.stat().st_size:,} bytes")
            print(f"  Modified file size: {modified_path.stat().st_size:,} bytes")
            print(f"  Number of differences: {len(differences)}")
            for line_num, orig, mod in differences:
                print(f"  Line {line_num}:")
                print(f"    - {orig[:100]}...")
                print(f"    + {mod[:100]}...")
    
    def test_add_and_remove_synset(self, oewn_lexicon):
        """Test that adding and removing a synset returns to original state."""
        from wn_edit import WordnetEditor
        
        lex_id = oewn_lexicon.id
        version = oewn_lexicon.version
        
        with tempfile.TemporaryDirectory() as tmpdir:
            original_path = Path(tmpdir) / "original.xml"
            roundtrip_path = Path(tmpdir) / "roundtrip.xml"
            
            # Export the original
            wn.export([oewn_lexicon], original_path)
            
            # Load into editor
            editor = WordnetEditor(f"{lex_id}:{version}")
            
            # Add a synset with:
            # - a new word that doesn't exist ('temporarytestword12345')
            # - an existing word ('test') to ensure its entry isn't deleted
            synset = editor.create_synset(
                pos='n',
                definition='A temporary test synset for round-trip testing',
                words=['temporarytestword12345', 'test'],
            )
            synset_id = synset['id']
            
            # Remove it - should remove the new entry but keep 'test' entry
            # (which has other senses)
            editor.remove_synset(synset_id)
            
            # Export
            editor.export(roundtrip_path)
            
            # Compare - should be identical
            original_lines = normalize_xml_for_comparison(original_path)
            roundtrip_lines = normalize_xml_for_comparison(roundtrip_path)
            
            differences = find_xml_differences(original_lines, roundtrip_lines)
            
            if differences:
                print(f"\nUnexpected differences found:")
                for line_num, orig, mod in differences[:10]:  # Show first 10
                    print(f"  Line {line_num}:")
                    print(f"    - {orig[:80]}")
                    print(f"    + {mod[:80]}")
                if len(differences) > 10:
                    print(f"  ... and {len(differences) - 10} more differences")
            
            assert len(differences) == 0, (
                f"Expected no differences after add/remove round-trip, "
                f"but found {len(differences)}"
            )
            
            print(f"\n✓ Add/remove round-trip test passed!")
            print(f"  Lexicon: {lex_id}:{version}")
            print(f"  File size: {original_path.stat().st_size:,} bytes")


class TestSmallWordnetRoundTrip:
    """Faster round-trip tests using smaller wordnets."""
    
    @pytest.fixture
    def small_lexicon(self):
        """Get a small lexicon for faster testing."""
        lexicons = wn.lexicons()
        if not lexicons:
            pytest.skip("No lexicons installed. Run: python -c \"import wn; wn.download('oewn:2024')\"")
        
        # Just return the first lexicon (for OEWN there's only one anyway)
        return lexicons[0]
    
    def test_metadata_change_roundtrip(self, small_lexicon):
        """Test changing metadata preserves everything else."""
        from wn_edit import WordnetEditor
        
        lex_id = small_lexicon.id
        version = small_lexicon.version
        
        with tempfile.TemporaryDirectory() as tmpdir:
            original_path = Path(tmpdir) / "original.xml"
            modified_path = Path(tmpdir) / "modified.xml"
            
            # Export original
            wn.export([small_lexicon], original_path)
            original_size = original_path.stat().st_size
            
            # Load and modify metadata
            editor = WordnetEditor(f"{lex_id}:{version}")
            original_label = editor.get_metadata().get('label', '')
            new_label = original_label + " (modified)"
            editor.set_label(new_label)
            
            # Export modified
            editor.export(modified_path)
            modified_size = modified_path.stat().st_size
            
            # Sizes should be very similar (just label change)
            size_diff = abs(modified_size - original_size)
            label_diff = len(new_label) - len(original_label)
            
            # Allow for some XML formatting differences
            assert size_diff < label_diff + 100, (
                f"File size changed too much: {original_size} -> {modified_size} "
                f"(diff: {size_diff}, expected ~{label_diff})"
            )
            
            print(f"\n✓ Metadata change test passed!")
            print(f"  Lexicon: {lex_id}:{version}")
            print(f"  Size change: {size_diff} bytes (label change: {label_diff} chars)")
