"""Mocule unit testing the Parser."""

from pathlib import Path

import pytest
from assembler.parser import Parser


@pytest.fixture(scope="function", name="mult_parser")
def fixture_mult_parser(mult_path: Path) -> Parser:
    """Return the parser where Mult.asm is loaded.

    Args:
        mult_path (Path): Path to Mult.asm

    Returns:
        Parser: Parser to Mult.asm
    """
    return Parser(str(mult_path))


def test_has_more_lines(mult_parser: Parser) -> None:
    """Test the functionality of Parser.has_more_lines.

    Args:
        mult_parser (Parser): Parser to Mult.asm
    """
    assert mult_parser.has_more_lines()
    while mult_parser.has_more_lines():
        mult_parser.advance()
    assert not mult_parser.has_more_lines()


def test_advance(mult_parser: Parser) -> None:
    """Test the functionality of Parser.advance.

    Args:
        mult_parser (Parser): Parser to Mult.asm
    """
    assert mult_parser.current_instruction is None
    mult_parser.advance()
    assert mult_parser.current_instruction == "@R0"
    mult_parser.advance()
    assert mult_parser.current_instruction == "D=M"
    while mult_parser.has_more_lines():
        mult_parser.advance()
    assert mult_parser.current_instruction == "0;JMP"
    mult_parser.advance()
    assert mult_parser.current_instruction is None


def test_instruction_type(mult_parser: Parser) -> None:
    """Test the functionality of Parser.instruction_type.

    Args:
        mult_parser (Parser): Parser to Mult.asm
    """
    mult_parser.advance()
    assert mult_parser.instruction_type() == "A_INSTRUCTION"
    mult_parser.advance()
    assert mult_parser.instruction_type() == "C_INSTRUCTION"
    # Label instruction at advance number 13
    for _ in range(13 - 2):
        mult_parser.advance()
    assert mult_parser.instruction_type() == "L_INSTRUCTION"


def test_symbol(mult_parser: Parser) -> None:
    """Test the functionality of Parser.symbol.

    Args:
        mult_parser (Parser): Parser to Mult.asm
    """
    # We mock the current instruction in this test
    mult_parser.current_instruction = "(LOOP)"
    assert mult_parser.symbol() == "LOOP"
    mult_parser.current_instruction = "@(2208)"
    assert mult_parser.symbol() == "2208"
    mult_parser.current_instruction = "@(cool)"
    assert mult_parser.symbol() == "cool"


def test_dest(mult_parser: Parser) -> None:
    """Test the functionality of Parser.dest.

    Args:
        mult_parser (Parser): Parser to Mult.asm
    """
    # We mock the current instruction in this test
    mult_parser.current_instruction = "@(2208)"
    assert mult_parser.dest() == ""
    mult_parser.current_instruction = "(LOOP)"
    assert mult_parser.dest() == ""
    mult_parser.current_instruction = "D"
    assert mult_parser.dest() == ""
    mult_parser.current_instruction = "D;JLE"
    assert mult_parser.dest() == ""
    mult_parser.current_instruction = "A=D;JLE"
    assert mult_parser.dest() == "A"
    mult_parser.current_instruction = "MD=M-1"
    assert mult_parser.dest() == "MD"


def test_comp(mult_parser: Parser) -> None:
    """Test the functionality of Parser.comp.

    Args:
        mult_parser (Parser): Parser to Mult.asm
    """
    # We mock the current instruction in this test
    mult_parser.current_instruction = "D"
    assert mult_parser.comp() == "D"
    mult_parser.current_instruction = "D;JLE"
    assert mult_parser.comp() == "D"
    mult_parser.current_instruction = "A=D|A;JLE"
    assert mult_parser.comp() == "D|A"
    mult_parser.current_instruction = "MD=M-1"
    assert mult_parser.comp() == "M-1"


def test_jump(mult_parser: Parser) -> None:
    """Test the functionality of Parser.jump.

    Args:
        mult_parser (Parser): Parser to Mult.asm
    """
    mult_parser.current_instruction = "D"
    assert mult_parser.jump() == ""
    mult_parser.current_instruction = "D;JLE"
    assert mult_parser.jump() == "JLE"
    mult_parser.current_instruction = "A=D|A;JEQ"
    assert mult_parser.jump() == "JEQ"
    mult_parser.current_instruction = "MD=M-1"
    assert mult_parser.jump() == ""
