"""Module containing test for the JackTokenizer."""

import io
from pathlib import Path

import pytest
from jack_compiler.jack_tokenizer import JackTokenizer


def test_has_more_tokens(data_path: Path) -> None:
    """Test that has_more_tokens return correct boolean.

    Args:
        data_path (Path): Path to the data path
    """
    with data_path.joinpath("Comments.jack").open(encoding="utf-8") as file:
        jack_tokenizer = JackTokenizer(file)
        assert jack_tokenizer.has_more_tokens()
        _ = jack_tokenizer.file.readlines()
        jack_tokenizer.cur_line = jack_tokenizer.file.readline()
        assert not jack_tokenizer.has_more_tokens()


def test__next_is_comment(data_path: Path) -> None:
    """Test that comments can be properly parsed.

    Args:
        data_path (Path): Path to the data path
    """
    # pylint: disable=too-many-statements,protected-access
    with data_path.joinpath("Comments.jack").open(encoding="utf-8") as file:
        jack_tokenizer = JackTokenizer(file)
        assert jack_tokenizer.cur_line == "// Start with\n"
        jack_tokenizer.match = jack_tokenizer.compiled_regex.match(
            jack_tokenizer.cur_line
        )
        assert jack_tokenizer._next_is_comment()
        assert jack_tokenizer.cur_line == "// two comments\n"
        jack_tokenizer.match = jack_tokenizer.compiled_regex.match(
            jack_tokenizer.cur_line
        )
        assert jack_tokenizer._next_is_comment()
        assert jack_tokenizer.cur_line == "\n"
        jack_tokenizer.match = jack_tokenizer.compiled_regex.match(
            jack_tokenizer.cur_line
        )
        assert not jack_tokenizer._next_is_comment()
        # NOTE: We must manually advance since we are at a newline
        jack_tokenizer.cur_line = jack_tokenizer.file.readline()

        assert jack_tokenizer.cur_line == "/* Followed by a block comment */\n"
        jack_tokenizer.match = jack_tokenizer.compiled_regex.match(
            jack_tokenizer.cur_line
        )
        assert jack_tokenizer._next_is_comment()
        # NOTE: In a block comment there may be tokens following */
        assert jack_tokenizer.cur_line == "\n"
        jack_tokenizer.match = jack_tokenizer.compiled_regex.match(
            jack_tokenizer.cur_line
        )
        assert not jack_tokenizer._next_is_comment()
        # NOTE: We must manually advance since we are at a newline
        jack_tokenizer.cur_line = jack_tokenizer.file.readline()
        assert jack_tokenizer.cur_line == "/*\n"
        jack_tokenizer.match = jack_tokenizer.compiled_regex.match(
            jack_tokenizer.cur_line
        )
        assert jack_tokenizer._next_is_comment()
        assert jack_tokenizer.cur_line == "\n"
        # NOTE: We must manually advance twice
        #       The first time since we've eaten *\
        #       The second time since we're at a blank new line
        jack_tokenizer.cur_line = jack_tokenizer.file.readline()
        jack_tokenizer.cur_line = jack_tokenizer.file.readline()

        assert jack_tokenizer.cur_line == "/** Followed by a docstring */\n"
        jack_tokenizer.match = jack_tokenizer.compiled_regex.match(
            jack_tokenizer.cur_line
        )
        assert jack_tokenizer._next_is_comment()
        assert jack_tokenizer.cur_line == "\n"
        jack_tokenizer.match = jack_tokenizer.compiled_regex.match(
            jack_tokenizer.cur_line
        )
        assert not jack_tokenizer._next_is_comment()
        # NOTE: We must manually advance since we are at a newline
        jack_tokenizer.cur_line = jack_tokenizer.file.readline()

        assert jack_tokenizer.cur_line == "class Comments {\n"
        jack_tokenizer.cur_line = jack_tokenizer.file.readline()
        assert jack_tokenizer.cur_line == "  // Which has some static variables\n"
        jack_tokenizer.match = jack_tokenizer.compiled_regex.match(
            jack_tokenizer.cur_line
        )
        assert jack_tokenizer._next_is_comment()

        assert (
            jack_tokenizer.cur_line
            == "  static int dummy;  // Which has a line comment\n"
        )
        jack_tokenizer.match = jack_tokenizer.compiled_regex.match(
            jack_tokenizer.cur_line
        )
        assert not jack_tokenizer._next_is_comment()
        jack_tokenizer._eat(jack_tokenizer.cur_line.find(";") + 1)
        assert jack_tokenizer.cur_line == "  // Which has a line comment\n"
        jack_tokenizer.match = jack_tokenizer.compiled_regex.match(
            jack_tokenizer.cur_line
        )
        assert jack_tokenizer._next_is_comment()

        assert (
            jack_tokenizer.cur_line
            == "  static int dummy2;  /* Which has a block comment **/\n"
        )
        jack_tokenizer.match = jack_tokenizer.compiled_regex.match(
            jack_tokenizer.cur_line
        )
        assert not jack_tokenizer._next_is_comment()
        jack_tokenizer._eat(jack_tokenizer.cur_line.find(";") + 1)
        jack_tokenizer.match = jack_tokenizer.compiled_regex.match(
            jack_tokenizer.cur_line
        )
        assert jack_tokenizer._next_is_comment()
        # NOTE: The cur line will be the leftover when */ is eaten
        assert jack_tokenizer.cur_line == "\n"
        jack_tokenizer.match = jack_tokenizer.compiled_regex.match(
            jack_tokenizer.cur_line
        )
        assert not jack_tokenizer._next_is_comment()
        jack_tokenizer.cur_line = jack_tokenizer.file.readline()

        assert jack_tokenizer.cur_line == "  static int dummy3;  /*\n"
        jack_tokenizer.match = jack_tokenizer.compiled_regex.match(
            jack_tokenizer.cur_line
        )
        assert not jack_tokenizer._next_is_comment()
        jack_tokenizer._eat(jack_tokenizer.cur_line.find(";") + 1)
        jack_tokenizer.match = jack_tokenizer.compiled_regex.match(
            jack_tokenizer.cur_line
        )
        assert jack_tokenizer._next_is_comment()
        # NOTE: The cur line will be the leftover when */ is eaten
        assert jack_tokenizer.cur_line == "\n"
        jack_tokenizer.match = jack_tokenizer.compiled_regex.match(
            jack_tokenizer.cur_line
        )
        assert not jack_tokenizer._next_is_comment()
        jack_tokenizer.cur_line = jack_tokenizer.file.readline()

        assert (
            jack_tokenizer.cur_line
            == "  static int /* even inline comments */ dummy4;\n"
        )
        jack_tokenizer.match = jack_tokenizer.compiled_regex.match(
            jack_tokenizer.cur_line
        )
        assert not jack_tokenizer._next_is_comment()
        before_comment = "int"
        jack_tokenizer._eat(
            jack_tokenizer.cur_line.find(before_comment) + len(before_comment)
        )
        assert jack_tokenizer.cur_line == " /* even inline comments */ dummy4;\n"
        jack_tokenizer.match = jack_tokenizer.compiled_regex.match(
            jack_tokenizer.cur_line
        )
        assert jack_tokenizer._next_is_comment()
        assert jack_tokenizer.cur_line == " dummy4;\n"
        jack_tokenizer.match = jack_tokenizer.compiled_regex.match(
            jack_tokenizer.cur_line
        )
        assert not jack_tokenizer._next_is_comment()
        jack_tokenizer.cur_line = jack_tokenizer.file.readline()

        assert jack_tokenizer.cur_line == "\n"
        jack_tokenizer.match = jack_tokenizer.compiled_regex.match(
            jack_tokenizer.cur_line
        )
        assert not jack_tokenizer._next_is_comment()
        jack_tokenizer.cur_line = jack_tokenizer.file.readline()

        assert jack_tokenizer.cur_line == "  function void noFunc(){ return; }\n"
        jack_tokenizer.match = jack_tokenizer.compiled_regex.match(
            jack_tokenizer.cur_line
        )
        assert not jack_tokenizer._next_is_comment()
        jack_tokenizer.cur_line = jack_tokenizer.file.readline()

        assert jack_tokenizer.cur_line == "}\n"
        jack_tokenizer.match = jack_tokenizer.compiled_regex.match(
            jack_tokenizer.cur_line
        )
        assert not jack_tokenizer._next_is_comment()

        # We should now be out of tokens
        jack_tokenizer.cur_line = jack_tokenizer.file.readline()
        assert jack_tokenizer.cur_line == ""
        assert not jack_tokenizer.has_more_tokens()


def test__eat() -> None:
    """Test that __eat eats correctly."""
    # pylint: disable=protected-access
    file = io.StringIO("Hello, world!")
    jack_tokenizer = JackTokenizer(file)
    assert jack_tokenizer.cur_line == "Hello, world!"
    jack_tokenizer._eat(len("Hello"))
    assert jack_tokenizer.cur_line == ", world!"
    jack_tokenizer._eat(len(", "))
    assert jack_tokenizer.cur_line == "world!"
    jack_tokenizer._eat(len("wo"))
    assert jack_tokenizer.cur_line == "rld!"
    jack_tokenizer._eat(len("rld!"))
    assert jack_tokenizer.cur_line == ""


def test_single_line_advance() -> None:
    """Test that advance advances over a single line."""
    file = io.StringIO("   Hello, world!")
    jack_tokenizer = JackTokenizer(file)
    with pytest.raises(Exception) as e_info:
        jack_tokenizer.advance()
    assert (
        e_info.value.args[0]
        == "Could not set cur_token as no matches were found, did you run has_more_lines first?"
    )
    assert jack_tokenizer.cur_line == "   Hello, world!"

    assert jack_tokenizer.has_more_tokens()
    assert jack_tokenizer.match.group(jack_tokenizer.match.lastgroup) == "Hello"  # type: ignore
    jack_tokenizer.advance()
    assert jack_tokenizer.cur_line == ", world!"

    assert jack_tokenizer.has_more_tokens()
    assert jack_tokenizer.match.group(jack_tokenizer.match.lastgroup) == ","  # type: ignore
    jack_tokenizer.advance()
    assert jack_tokenizer.cur_line == " world!"

    assert jack_tokenizer.has_more_tokens()
    assert jack_tokenizer.match.group(jack_tokenizer.match.lastgroup) == "world"  # type: ignore
    jack_tokenizer.advance()
    assert jack_tokenizer.cur_line == "!"

    # NOTE: "!" is not a valid token
    assert not jack_tokenizer.has_more_tokens()
    assert jack_tokenizer.match is None
    with pytest.raises(Exception) as e_info:
        jack_tokenizer.advance()
    assert (
        e_info.value.args[0]
        == "Could not set cur_token as no matches were found, did you run has_more_lines first?"
    )
    assert jack_tokenizer.cur_line == ""


def test_multi_line_advance() -> None:
    """Test that advance advances over a multiple lines."""
    tokens = (
        "Hello",
        ",",
        "world",
        "foo",
        "=",
        "42",
        "bar",
        "=",
        "shoot",
        "DONE",
    )
    file = io.StringIO(
        f"   {tokens[0]}{tokens[1]} {tokens[2]}!\n"
        f"{tokens[3]} {tokens[4]} {tokens[5]} // My comment\n"
        "\n"
        f'{tokens[6]}{tokens[7]}"{tokens[8]}"\n'
        "/* Multi line\n"
        " * comment\n"
        " */\n"
        "\n"
        "\n"
        f"{tokens[9]}\n"
    )
    jack_tokenizer = JackTokenizer(file)
    for token in tokens:
        assert jack_tokenizer.has_more_tokens()
        jack_tokenizer.advance()
        assert jack_tokenizer.cur_token == token


def test_token_type() -> None:
    """Test that token_type identifies the correct types."""
    file = io.StringIO('  class = world 5234 "This is a string"')
    jack_tokenizer = JackTokenizer(file)
    assert jack_tokenizer.cur_line == '  class = world 5234 "This is a string"'
    assert jack_tokenizer.has_more_tokens()
    assert jack_tokenizer.token_type() == "KEYWORD"

    jack_tokenizer.advance()
    assert jack_tokenizer.cur_line == ' = world 5234 "This is a string"'
    assert jack_tokenizer.has_more_tokens()
    assert jack_tokenizer.token_type() == "SYMBOL"

    jack_tokenizer.advance()
    assert jack_tokenizer.cur_line == ' world 5234 "This is a string"'
    assert jack_tokenizer.has_more_tokens()
    assert jack_tokenizer.token_type() == "IDENTIFIER"

    jack_tokenizer.advance()
    assert jack_tokenizer.cur_line == ' 5234 "This is a string"'
    assert jack_tokenizer.has_more_tokens()
    assert jack_tokenizer.token_type() == "INT_CONST"

    jack_tokenizer.advance()
    assert jack_tokenizer.cur_line == ' "This is a string"'

    assert jack_tokenizer.has_more_tokens()
    assert jack_tokenizer.token_type() == "STRING_CONST"


def test_keyword() -> None:
    """Test that all keywords work."""
    keywords = JackTokenizer.keywords
    keywords_str = " ".join(keywords)
    file = io.StringIO(keywords_str)
    jack_tokenizer = JackTokenizer(file)

    for keyword in keywords:
        assert jack_tokenizer.has_more_tokens()
        jack_tokenizer.advance()
        assert jack_tokenizer.token_type() == "KEYWORD"
        assert jack_tokenizer.keyword() == keyword.upper()


def test_symbol() -> None:
    """Test that all symbols work."""
    symbols = JackTokenizer.symbols
    symbols_str = " ".join(symbols)
    file = io.StringIO(symbols_str)
    jack_tokenizer = JackTokenizer(file)

    for symbol in symbols:
        assert jack_tokenizer.has_more_tokens()
        jack_tokenizer.advance()
        assert jack_tokenizer.token_type() == "SYMBOL"
        assert jack_tokenizer.symbol() == symbol.upper()


def test_identifier() -> None:
    """Test that identifier work."""
    identifiers = ("foo", "bar", "baz")
    identifiers_str = " ".join(identifiers)
    file = io.StringIO(identifiers_str)
    jack_tokenizer = JackTokenizer(file)

    for identifier in identifiers:
        assert jack_tokenizer.has_more_tokens()
        jack_tokenizer.advance()
        assert jack_tokenizer.token_type() == "IDENTIFIER"
        assert jack_tokenizer.identifier() == identifier


def test_int_val() -> None:
    """Test that int_val work."""
    int_vals = (1, 20, 99999, 9999999)
    int_val_str = " ".join([str(integer) for integer in int_vals])
    file = io.StringIO(int_val_str)
    jack_tokenizer = JackTokenizer(file)

    for int_val in int_vals[:-1]:
        assert jack_tokenizer.has_more_tokens()
        jack_tokenizer.advance()
        assert jack_tokenizer.token_type() == "INT_CONST"
        assert jack_tokenizer.int_val() == int_val

    # We only capture 5 digits, hence the last digit will not be captured
    int_val = int_vals[-1]
    assert jack_tokenizer.has_more_tokens()
    jack_tokenizer.advance()
    assert jack_tokenizer.token_type() == "INT_CONST"
    assert jack_tokenizer.int_val() != int_val


def test_string_val() -> None:
    """Test that string_val work."""
    string_vals = (
        '"foo"',
        '"bar"\n',
        '"baz"\n',
        '"My super long string with symbols and class *(&=|"\n',
    )
    string_vals_str = " ".join(string_vals)
    file = io.StringIO(string_vals_str)
    jack_tokenizer = JackTokenizer(file)

    for string_val in string_vals:
        assert jack_tokenizer.has_more_tokens()
        jack_tokenizer.advance()
        assert jack_tokenizer.token_type() == "STRING_CONST"
        assert jack_tokenizer.string_val() == string_val.replace('"', "").replace(
            "\n", ""
        )
