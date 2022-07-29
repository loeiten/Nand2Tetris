"""Module containing test for the CompilationEngine."""
# pylint: disable=protected-access

from pathlib import Path

import pytest
from jack_compiler.compilation_engine import CompilationEngine
from jack_compiler.jack_tokenizer import JackTokenizer


@pytest.mark.parametrize("test_name", ("ClassVarDec1", "ClassVarDec2", "ClassVarDec3"))
def test_class_var_dec(tmp_path: Path, data_path: Path, test_name: str) -> None:
    """Test the class_var_dec function.

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
            # The compilation engine assumes that we have advanced
            assert jack_tokenizer.has_more_tokens()
            compilation_engine._advance()
            compilation_engine.compile_class_var_dec()

            if jack_tokenizer.has_more_tokens():
                compilation_engine._advance()
                compilation_engine.compile_class_var_dec()

    with data_path.joinpath(f"{test_name}.xml").open(encoding="utf-8") as expected_file:
        expected = expected_file.readlines()

    with tmp_path.joinpath(f"{test_name}.xml").open(encoding="utf-8") as result_file:
        result = result_file.readlines()

    assert expected == result


# FIXME: Start testing from terminal statements
# FIXME: Add recursive testing
# FIXME: Do not start grammar if starred expression (see classVarDec of ArrayTest as an example)
# FIXME: Make a test of this
