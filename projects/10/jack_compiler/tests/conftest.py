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


@pytest.fixture(scope="session", name="array_test_path")
def fixture_array_test_path() -> Path:
    """Return the path to the ArrayTest directory.

    Returns:
        Path: Path to the ArrayTest directory
    """
    return Path(__file__).parents[2].joinpath("ArrayTest").resolve()


@pytest.fixture(scope="session", name="expression_less_square_path")
def fixture_expression_less_square_path() -> Path:
    """Return the path to the ExpressionLessSquare directory.

    Returns:
        Path: Path to the ExpressionLessSquare directory
    """
    return Path(__file__).parents[2].joinpath("ExpressionLessSquare").resolve()


@pytest.fixture(scope="session", name="square_path")
def fixture_square_path() -> Path:
    """Return the path to the Square directory.

    Returns:
        Path: Path to the Square directory
    """
    return Path(__file__).parents[2].joinpath("Square").resolve()
