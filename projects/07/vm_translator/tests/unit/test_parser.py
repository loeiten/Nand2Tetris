"""Module unit testing the Parser."""

from pathlib import Path

import pytest
from vm_translator.parser import Parser


@pytest.fixture(scope="function", name="full_test_parser")
def fixture_full_test_parser(full_test_path: Path) -> Parser:
    """Return the parser where FullTest.vm is loaded.

    Args:
        full_test_path (Path): Path to FullTest.vm

    Returns:
        Parser: Parser to FullTest.vm
    """
    return Parser(str(full_test_path))


def test_has_more_commands(full_test_parser: Parser) -> None:
    """Test the functionality of Parser.has_more_commands.

    Args:
        full_test_parser (Parser): Parser to FullTest.vm
    """
    assert full_test_parser.has_more_commands()
    while full_test_parser.has_more_commands():
        full_test_parser.advance()
    assert not full_test_parser.has_more_commands()


def test_advance(full_test_parser: Parser) -> None:
    """Test the functionality of Parser.advance.

    Args:
        full_test_parser (Parser): Parser to FullTest.vm
    """
    assert full_test_parser.current_instruction == ""
    full_test_parser.advance()
    assert full_test_parser.current_instruction == "push constant 0"
    full_test_parser.advance()
    assert full_test_parser.current_instruction == "push constant 1"
    while full_test_parser.has_more_commands():
        full_test_parser.advance()
    assert full_test_parser.current_instruction == "not"
    full_test_parser.advance()
    assert full_test_parser.current_instruction == ""


def test_command_type(full_test_parser: Parser) -> None:
    """Test the functionality of Parser.command_type.

    Args:
        full_test_parser (Parser): Parser to FullTest.vm
    """
    full_test_parser.advance()
    assert full_test_parser.command_type() == "C_PUSH"
    for _ in range(9):
        full_test_parser.advance()
    assert full_test_parser.command_type() == "C_POP"
    for _ in range(2):
        full_test_parser.advance()
    assert full_test_parser.command_type() == "C_ARITHMETIC"


def test_arg1(full_test_parser: Parser) -> None:
    """Test the functionality of Parser.arg1.

    Args:
        full_test_parser (Parser): Parser to FullTest.vm
    """
    full_test_parser.advance()
    assert full_test_parser.arg1() == "constant"
    for _ in range(9):
        full_test_parser.advance()
    assert full_test_parser.arg1() == "local"
    for _ in range(2):
        full_test_parser.advance()
    assert full_test_parser.arg1() == "add"


def test_arg2(full_test_parser: Parser) -> None:
    """Test the functionality of Parser.arg2.

    Args:
        full_test_parser (Parser): Parser to FullTest.vm
    """
    full_test_parser.advance()
    assert full_test_parser.arg2() == 0
    for _ in range(9):
        full_test_parser.advance()
    assert full_test_parser.arg2() == 2
