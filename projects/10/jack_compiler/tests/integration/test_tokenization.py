"""Test tokenization."""

from pathlib import Path
from typing import Callable, Dict, Literal, Tuple, get_args

import pytest
from jack_compiler.jack_analyzer import process_file

TestNames = Literal["array_test", "expression_less_square", "square"]
TestFiles = Literal["in_path", "expected_path", "out_path"]


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
                "expected_path": array_test_path.joinpath("MainT.xml"),
                "out_path": tmp_path.joinpath("MainT.xml"),
            },
        ),
        "expression_less_square": (
            {
                "in_path": expression_less_square_path.joinpath("Main.jack"),
                "expected_path": expression_less_square_path.joinpath("MainT.xml"),
                "out_path": tmp_path.joinpath("MainT.xml"),
            },
            {
                "in_path": expression_less_square_path.joinpath("Square.jack"),
                "expected_path": expression_less_square_path.joinpath("SquareT.xml"),
                "out_path": tmp_path.joinpath("SquareT.xml"),
            },
            {
                "in_path": expression_less_square_path.joinpath("SquareGame.jack"),
                "expected_path": expression_less_square_path.joinpath(
                    "SquareGameT.xml"
                ),
                "out_path": tmp_path.joinpath("SquareGameT.xml"),
            },
        ),
        "square": (
            {
                "in_path": square_path.joinpath("Main.jack"),
                "expected_path": square_path.joinpath("MainT.xml"),
                "out_path": tmp_path.joinpath("MainT.xml"),
            },
            {
                "in_path": square_path.joinpath("Square.jack"),
                "expected_path": square_path.joinpath("SquareT.xml"),
                "out_path": tmp_path.joinpath("SquareT.xml"),
            },
            {
                "in_path": square_path.joinpath("SquareGame.jack"),
                "expected_path": square_path.joinpath("SquareGameT.xml"),
                "out_path": tmp_path.joinpath("SquareGameT.xml"),
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


@pytest.mark.parametrize("name", get_args(TestNames))
def test_array_test(
    get_paths: Callable[[TestNames], Tuple[Dict[TestFiles, Path], ...]],
    name: TestNames,
) -> None:
    """Test that the output of the jack compiler matches that of ArrayTest.

    Args:
        get_paths (Callable[[TestNames], Tuple[Dict[TestFiles, Path], ...]]):
            Paths to the input, temp-files and expected output files
        name (TestNames):
            Name of the paths to return
    """
    test_path_groups = get_paths(name)
    for test_path_group in test_path_groups:
        in_path = test_path_group["in_path"]
        expected_path = test_path_group["expected_path"]
        out_path = test_path_group["out_path"]

        process_file(in_path=in_path, tokens_only=True, out_path=out_path)
        with out_path.open("r+") as out_file:
            lines = out_file.readlines()
            lines.insert(0, "<tokens>\n")
            lines.append("</tokens>\n")
            out_file.seek(0)
            out_file.writelines(lines)

        with expected_path.open("r", encoding="utf-8") as expected_file:
            expected_lines = expected_file.readlines()

        with out_path.open("r", encoding="utf-8") as out_file:
            out_lines = out_file.readlines()

        assert expected_lines == out_lines
