"""Module containing global fixtures."""

from pathlib import Path
from typing import Callable, Dict, Tuple

import pytest
from tests import TestFiles, TestNames


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


@pytest.fixture(scope="function", name="get_paths")
def fixture_get_paths(
    tmp_path: Path,
    array_test_path: Path,
    expression_less_square_path: Path,
    square_path: Path,
) -> Callable[[TestNames], Tuple[Dict[TestFiles, Path], ...]]:
    """Return the get paths function.

    Args:
        tmp_path (Path): Path to temporary directory
        array_test_path (Path): Path to the ArrayTest directory
        expression_less_square_path (Path): Path to the ExpressionLessSquare directory
        square_path (Path): Path to the Square directory

    Returns:
        Callable[[TestNames], Tuple[Dict[TestFiles, Path], ...]]:
            Function which returns the paths
    """
    name_map: Dict[TestNames, Tuple[Dict[TestFiles, Path], ...]] = {
        "array_test": (
            {
                "in_path": array_test_path.joinpath("Main.jack"),
                "expected_token_path": array_test_path.joinpath("MainT.xml"),
                "out_token_path": tmp_path.joinpath("MainT.xml"),
                "expected_path": array_test_path.joinpath("Main.xml"),
                "out_path": tmp_path.joinpath("Main.xml"),
            },
        ),
        "expression_less_square": (
            {
                "in_path": expression_less_square_path.joinpath("Main.jack"),
                "expected_token_path": expression_less_square_path.joinpath(
                    "MainT.xml"
                ),
                "out_token_path": tmp_path.joinpath("MainT.xml"),
                "expected_path": expression_less_square_path.joinpath("Main.xml"),
                "out_path": tmp_path.joinpath("Main.xml"),
            },
            {
                "in_path": expression_less_square_path.joinpath("Square.jack"),
                "expected_token_path": expression_less_square_path.joinpath(
                    "SquareT.xml"
                ),
                "out_token_path": tmp_path.joinpath("SquareT.xml"),
                "expected_path": expression_less_square_path.joinpath("Square.xml"),
                "out_path": tmp_path.joinpath("Square.xml"),
            },
            {
                "in_path": expression_less_square_path.joinpath("SquareGame.jack"),
                "expected_token_path": expression_less_square_path.joinpath(
                    "SquareGameT.xml"
                ),
                "out_token_path": tmp_path.joinpath("SquareGameT.xml"),
                "expected_path": expression_less_square_path.joinpath("SquareGame.xml"),
                "out_path": tmp_path.joinpath("SquareGame.xml"),
            },
        ),
        "square": (
            {
                "in_path": square_path.joinpath("Main.jack"),
                "expected_token_path": square_path.joinpath("MainT.xml"),
                "out_token_path": tmp_path.joinpath("MainT.xml"),
                "expected_path": square_path.joinpath("Main.xml"),
                "out_path": tmp_path.joinpath("Main.xml"),
            },
            {
                "in_path": square_path.joinpath("Square.jack"),
                "expected_token_path": square_path.joinpath("SquareT.xml"),
                "out_token_path": tmp_path.joinpath("SquareT.xml"),
                "expected_path": square_path.joinpath("Square.xml"),
                "out_path": tmp_path.joinpath("Square.xml"),
            },
            {
                "in_path": square_path.joinpath("SquareGame.jack"),
                "expected_token_path": square_path.joinpath("SquareGameT.xml"),
                "out_token_path": tmp_path.joinpath("SquareGameT.xml"),
                "expected_path": square_path.joinpath("SquareGame.xml"),
                "out_path": tmp_path.joinpath("SquareGame.xml"),
            },
        ),
    }

    def _get_paths(name: TestNames) -> Tuple[Dict[TestFiles, Path], ...]:
        """Return the paths corresponding to input.

        Args:
            name (TestNames):
                Name of the paths to return

        Returns:
            Tuple[Dict[TestFiles, Path], ...]:
                The Paths corresponding to the name
        """
        return name_map[name]

    return _get_paths
