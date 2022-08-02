"""Module containing test for the CompilationEngine."""
# pylint: disable=protected-access

from pathlib import Path
from typing import Tuple

import pytest
from jack_compiler.compilation_engine import CompilationEngine
from jack_compiler.jack_tokenizer import JackTokenizer


def merge_tuple(
    names: Tuple[str, ...], function_name: str
) -> Tuple[Tuple[str, str], ...]:
    """Merge a tuple of string with another string.

    Args:
        names (Tuple[str, ...]): Tuple to merge
        function_name (str): String to merge with

    Returns:
        Tuple[Tuple[str, str], ...]: Merged tuple
    """
    return tuple((name, function_name) for name in names)


CLASS_VAR_DEC = merge_tuple(
    ("ClassVarDec1", "ClassVarDec2", "ClassVarDec3"), "compile_class_var_dec"
)
TERM = merge_tuple(("term",), "compile_term")


@pytest.mark.parametrize("test_name, function_name", CLASS_VAR_DEC + TERM)
def test_compile_functions(
    tmp_path: Path, data_path: Path, test_name: str, function_name: str
) -> None:
    """Test the various compile functions.

    In order to run only one compile function one can use::

        $ pytest -xsvv --ff -k name_of_function

    Args:
        tmp_path (Path): Path to temporary directory
        data_path (Path): Path to the data path
        test_name (str): Name of the test
        function_name (str): Name of function to call
    """
    with data_path.joinpath(f"{test_name}.jack").open(encoding="utf-8") as in_file:
        jack_tokenizer = JackTokenizer(in_file=in_file)

        with tmp_path.joinpath(f"{test_name}.xml").open("w") as out_file:
            compilation_engine = CompilationEngine(
                jack_tokenizer=jack_tokenizer, out_file=out_file
            )
            func = getattr(compilation_engine, function_name)
            while jack_tokenizer.has_more_tokens():
                # The compilation engine assumes that we have advanced
                compilation_engine._advance()
                func()

    with data_path.joinpath(f"{test_name}.xml").open(encoding="utf-8") as expected_file:
        expected = expected_file.readlines()

    with tmp_path.joinpath(f"{test_name}.xml").open(encoding="utf-8") as result_file:
        result = result_file.readlines()

    assert expected == result


# FIXME: pytest -xsvv --ff
# FIXME: YOU ARE HERE: Next up: expression, expressionList, statements, program structure
# FIXME: Start testing from terminal statements
# FIXME: Add recursive testing
# FIXME: Do not start grammar if starred expression (see classVarDec of ArrayTest as an example)
# FIXME: Make a test of this
