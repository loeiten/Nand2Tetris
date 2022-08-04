"""Test compilation."""

from pathlib import Path
from typing import Callable, Dict, Tuple, get_args

import pytest
from jack_compiler.jack_analyzer import process_file
from tests import TestFiles, TestNames


@pytest.mark.parametrize("name", get_args(TestNames))
def test_tokenization(
    get_paths: Callable[[TestNames], Tuple[Dict[TestFiles, Path], ...]],
    name: TestNames,
) -> None:
    """Test that the output of the jack compiler matches that of the files.

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

        process_file(in_path=in_path, tokens_only=False, out_path=out_path)

        with expected_path.open("r", encoding="utf-8") as expected_file:
            expected_lines = expected_file.readlines()

        with out_path.open("r", encoding="utf-8") as out_file:
            out_lines = out_file.readlines()

        assert expected_lines == out_lines
