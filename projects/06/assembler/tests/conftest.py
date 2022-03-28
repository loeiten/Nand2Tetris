"""Module containing global fixtures."""

from pathlib import Path

import pytest


@pytest.fixture(scope="session")
def mult_path() -> Path:
    """Return the path to Rect.asm.

    Returns:
        Path: Path to Rect.asm
    """
    return Path(__file__).parent.joinpath("data", "Mult.asm").resolve()
