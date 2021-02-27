"""Define some fixtures."""

from pathlib import Path

import pytest

@pytest.fixture
def output_dir():
    """Static output directory."""
    return str(
        Path(__file__).resolve().parent / Path("data")
    )
