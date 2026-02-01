"""Shared test configuration and fixtures."""

import pytest
from pathlib import Path

try:
    import wn
    HAS_WN = True
except ImportError:
    HAS_WN = False

# Local data directory for wn (avoids issues with the global ~/.wn_data cache)
WN_DATA_DIR = Path(__file__).resolve().parent.parent / ".wn_data"


@pytest.fixture(autouse=True, scope="session")
def _use_local_wn_data():
    """Configure wn to use a project-local data directory for all tests."""
    if not HAS_WN:
        yield
        return
    original_dir = wn.config.data_directory
    WN_DATA_DIR.mkdir(exist_ok=True)
    wn.config.data_directory = WN_DATA_DIR
    yield
    wn.config.data_directory = original_dir
