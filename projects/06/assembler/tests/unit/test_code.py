"""Module testing the Code class."""

from assembler.code import Code


def test_dest() -> None:
    """Test the functionality of Code.dest."""
    code = Code()
    assert code.dest("") == "000"
    assert code.dest("null") == "000"
    assert code.dest("M") == "001"
    assert code.dest("D") == "010"
    assert code.dest("A") == "100"


def test_comp() -> None:
    """Test the functionality of Code.comp."""
    code = Code()
    assert code.comp("0") == "0101010"
    assert code.comp("1") == "0111111"
    assert code.comp("A") == "0110000"
    assert code.comp("M") == "1110000"
    assert code.comp("D|A") == "0010101"
    assert code.comp("D|M") == "1010101"


def test_jump() -> None:
    """Test the functionality of Code.jump."""
    code = Code()
    assert code.jump("") == "000"
    assert code.jump("null") == "000"
    assert code.jump("JGT") == "001"
    assert code.jump("JEQ") == "010"
    assert code.jump("JLT") == "100"
    assert code.jump("JMP") == "111"
