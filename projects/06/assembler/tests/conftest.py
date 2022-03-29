"""Module containing global fixtures."""

from pathlib import Path

import pytest


@pytest.fixture(scope="session", name="data_path")
def fixture_data_path() -> Path:
    """Return the path to the data directory.

    Returns:
        Path: Path to the data directory
    """
    return Path(__file__).parent.joinpath("data").resolve()


@pytest.fixture(scope="session")
def mult_path(data_path: Path) -> Path:
    """Return the path to Mult.asm.

    Args:
        data_path (Path): Path to the data directory

    Returns:
        Path: Path to Mult.asm
    """
    return data_path.joinpath("Mult.asm")


@pytest.fixture(scope="session")
def fill_path(data_path: Path) -> Path:
    """Return the path to Fill.asm.

    Args:
        data_path (Path): Path to the data directory

    Returns:
        Path: Path to Fill.asm
    """
    return data_path.joinpath("Fill.asm")
