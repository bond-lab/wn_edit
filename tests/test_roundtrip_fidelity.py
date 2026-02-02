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


@pytest.fixture(scope="module")
def oewn_baseline(tmp_path_factory):
    """Export OEWN once and cache the XML + normalized lines for all tests.

    Downloads OEWN if not already installed. Returns a dict with:
      - lexicon: the wn.Lexicon object
      - xml_path: Path to the exported XML
      - normalized_lines: pre-normalized lines for comparison
    """
    if not HAS_WN:
        pytest.skip("wn package not installed")

    try:
        wn.download('oewn:2025')
    except Exception as e:
        print(f"Download note: {e}")

    lexicons = wn.lexicons()
    oewn = None
    for lex in lexicons:
        if lex.id.startswith('oewn') or lex.id.startswith('ewn'):
            oewn = lex
            break

    if oewn is None:
        if lexicons:
            pytest.skip(f"No OEWN found. Available: {[l.id for l in lexicons]}")
        else:
            pytest.skip("No lexicons installed. Run: python -c \"import wn; wn.download('oewn:2025')\"")

    xml_path = tmp_path_factory.mktemp("oewn_baseline") / "original.xml"
    wn.export([oewn], xml_path)
    normalized = normalize_xml_for_comparison(xml_path)

    return {
        'lexicon': oewn,
        'xml_path': xml_path,
        'normalized_lines': normalized,
    }


class TestRoundTripFidelity:
    """Test that round-trip editing preserves data fidelity."""

    def test_version_change_only(self, oewn_baseline):
        """Test that changing only the version produces minimal XML diff."""
        from wn_edit import WordnetEditor

        oewn = oewn_baseline['lexicon']
        original_lines = oewn_baseline['normalized_lines']
        lex_id = oewn.id
        original_version = oewn.version
        new_version = original_version + "-test"

        with tempfile.TemporaryDirectory() as tmpdir:
            modified_path = Path(tmpdir) / "modified.xml"

            editor = WordnetEditor(f"{lex_id}:{original_version}")
            editor.set_version(new_version)
            editor.export(modified_path)

            modified_lines = normalize_xml_for_comparison(modified_path)
            differences = find_xml_differences(original_lines, modified_lines)

            assert len(differences) > 0, "Expected at least one difference (version change)"

            for line_num, orig, mod in differences:
                assert 'version=' in orig or 'version=' in mod, (
                    f"Unexpected difference at line {line_num}:\n"
                    f"  Original: {orig}\n"
                    f"  Modified: {mod}"
                )
                if 'version=' in orig and 'version=' in mod:
                    assert original_version in orig, f"Original version not found in: {orig}"
                    assert new_version in mod, f"New version not found in: {mod}"

            print(f"\n  Lexicon: {lex_id}:{original_version}")
            print(f"  Differences: {len(differences)}")

    def test_add_and_remove_synset(self, oewn_baseline):
        """Test that adding and removing a synset returns to original state."""
        from wn_edit import WordnetEditor

        oewn = oewn_baseline['lexicon']
        original_lines = oewn_baseline['normalized_lines']
        lex_id = oewn.id
        version = oewn.version

        with tempfile.TemporaryDirectory() as tmpdir:
            roundtrip_path = Path(tmpdir) / "roundtrip.xml"

            editor = WordnetEditor(f"{lex_id}:{version}")

            synset = editor.create_synset(
                pos='n',
                definition='A temporary test synset for round-trip testing',
                words=['temporarytestword12345', 'test'],
            )
            editor.remove_synset(synset['id'])
            editor.export(roundtrip_path)

            roundtrip_lines = normalize_xml_for_comparison(roundtrip_path)
            differences = find_xml_differences(original_lines, roundtrip_lines)

            if differences:
                print(f"\nUnexpected differences found:")
                for line_num, orig, mod in differences[:10]:
                    print(f"  Line {line_num}:")
                    print(f"    - {orig[:80]}")
                    print(f"    + {mod[:80]}")
                if len(differences) > 10:
                    print(f"  ... and {len(differences) - 10} more differences")

            assert len(differences) == 0, (
                f"Expected no differences after add/remove round-trip, "
                f"but found {len(differences)}"
            )

    def test_metadata_change_roundtrip(self, oewn_baseline):
        """Test changing metadata preserves everything else."""
        from wn_edit import WordnetEditor

        oewn = oewn_baseline['lexicon']
        lex_id = oewn.id
        version = oewn.version
        original_size = oewn_baseline['xml_path'].stat().st_size

        with tempfile.TemporaryDirectory() as tmpdir:
            modified_path = Path(tmpdir) / "modified.xml"

            editor = WordnetEditor(f"{lex_id}:{version}")
            original_label = editor.get_metadata().get('label', '')
            new_label = original_label + " (modified)"
            editor.set_label(new_label)
            editor.export(modified_path)

            modified_size = modified_path.stat().st_size
            size_diff = abs(modified_size - original_size)
            label_diff = len(new_label) - len(original_label)

            assert size_diff < label_diff + 100, (
                f"File size changed too much: {original_size} -> {modified_size} "
                f"(diff: {size_diff}, expected ~{label_diff})"
            )

            print(f"\n  Size change: {size_diff} bytes (label change: {label_diff} chars)")

    def test_xml_fallback_roundtrip(self, oewn_baseline):
        """Test that the XML fallback path produces identical output to wn.export()."""
        from wn_edit import WordnetEditor

        oewn = oewn_baseline['lexicon']
        original_lines = oewn_baseline['normalized_lines']
        specifier = f"{oewn.id}:{oewn.version}"

        editor = WordnetEditor(create_new=True, lexicon_id="dummy")
        editor._resource = editor._load_from_database_xml(specifier)
        editor._lexicon = editor._resource['lexicons'][0]

        with tempfile.TemporaryDirectory() as tmpdir:
            xml_path = Path(tmpdir) / "xml_fallback.xml"
            from wn import lmf
            lmf.dump(editor._resource, xml_path)

            xml_lines = normalize_xml_for_comparison(xml_path)
            differences = find_xml_differences(original_lines, xml_lines)

            if differences:
                print(f"\nUnexpected differences:")
                for line_num, orig, mod in differences[:10]:
                    print(f"  Line {line_num}:")
                    print(f"    - {orig[:80]}")
                    print(f"    + {mod[:80]}")

            assert len(differences) == 0, (
                f"XML fallback path produced {len(differences)} differences vs wn.export()"
            )
