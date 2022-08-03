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


TERM = merge_tuple(("term",), "compile_term")
EXPRESSION_LIST = merge_tuple(
    ("expressionList1", "expressionList2"), "compile_expression_list"
)
EXPRESSION = merge_tuple(("expression1", "expression2"), "compile_expression")
RETURN_STATEMENT = merge_tuple(("returnStatement",), "compile_return")
DO_STATEMENT = merge_tuple(("doStatement",), "compile_do")
WHILE_STATEMENT = merge_tuple(("whileStatement1", "whileStatement2"), "compile_while")
IF_STATEMENT = merge_tuple(("ifStatement1", "ifStatement2"), "compile_if")
LET_STATEMENT = merge_tuple(("letStatement",), "compile_let")
VAR_DEC = merge_tuple(("varDec",), "compile_var_dec")
SUBROUTINE_BODY = merge_tuple(
    ("subroutineBody1", "subroutineBody2"), "compile_subroutine_body"
)
PARAMETER_LIST = merge_tuple(("parameterList",), "compile_parameter_list")
SUBROUTINE_DEC = merge_tuple(
    ("subroutineDec1", "subroutineDec2"), "compile_subroutine_dec"
)
CLASS_VAR_DEC = merge_tuple(
    ("classVarDec1", "classVarDec2", "classVarDec3"), "compile_class_var_dec"
)


@pytest.mark.parametrize(
    "test_name, function_name",
    TERM
    + EXPRESSION_LIST
    + EXPRESSION
    + RETURN_STATEMENT
    + DO_STATEMENT
    + WHILE_STATEMENT
    + IF_STATEMENT
    + LET_STATEMENT
    + VAR_DEC
    + SUBROUTINE_BODY
    + PARAMETER_LIST
    + SUBROUTINE_DEC
    + CLASS_VAR_DEC,
)
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


@pytest.mark.parametrize("test_name", ("class1", "class2", "class3"))
def test_class_compile(tmp_path: Path, data_path: Path, test_name: str) -> None:
    """Test the class compile function.

    Args:
        tmp_path (Path): Path to temporary directory
        data_path (Path): Path to the data path
        test_name (str): Name of the test
    """
    with data_path.joinpath(f"{test_name}.jack").open(encoding="utf-8") as in_file:
        jack_tokenizer = JackTokenizer(in_file=in_file)

        with tmp_path.joinpath(f"{test_name}.xml").open("w") as out_file:
            compilation_engine = CompilationEngine(
                jack_tokenizer=jack_tokenizer, out_file=out_file
            )
            compilation_engine.compile_class()

    with data_path.joinpath(f"{test_name}.xml").open(encoding="utf-8") as expected_file:
        expected = expected_file.readlines()

    with tmp_path.joinpath(f"{test_name}.xml").open(encoding="utf-8") as result_file:
        result = result_file.readlines()

    assert expected == result
