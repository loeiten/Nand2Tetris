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
def full_test_path(data_path: Path) -> Path:
    """Return the path to FullTest.vm.

    Args:
        data_path (Path): Path to the data directory

    Returns:
        Path: Path to FullTest.vm
    """
    return data_path.joinpath("FullTest.vm")
