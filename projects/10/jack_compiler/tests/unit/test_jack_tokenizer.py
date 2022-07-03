"""Module containing test for the JackTokenizer."""

from pathlib import Path

from jack_compiler.jack_tokenizer import JackTokenizer


def test_comment(data_path: Path) -> None:
    """Test that comments can be properly parsed.

    Args:
        data_path (Path): Path to the data path
    """
    # pylint: disable=too-many-statements
    with data_path.joinpath("Comments.jack").open(encoding="utf-8") as file:
        jack_tokenizer = JackTokenizer(file)
        assert jack_tokenizer.cur_line == "// Start with\n"
        assert jack_tokenizer.next_is_comment()
        assert jack_tokenizer.cur_line == "// two comments\n"
        assert jack_tokenizer.next_is_comment()
        assert jack_tokenizer.cur_line == "\n"
        assert not jack_tokenizer.next_is_comment()
        # NOTE: We must manually advance since we are at a newline
        jack_tokenizer.cur_line = jack_tokenizer.file.readline()

        assert jack_tokenizer.cur_line == "/* Followed by a block comment */\n"
        assert jack_tokenizer.next_is_comment()
        # NOTE: In a block comment there may be tokens following */
        assert jack_tokenizer.cur_line == "\n"
        assert not jack_tokenizer.next_is_comment()
        # NOTE: We must manually advance since we are at a newline
        jack_tokenizer.cur_line = jack_tokenizer.file.readline()
        assert jack_tokenizer.cur_line == "/*\n"
        assert jack_tokenizer.next_is_comment()
        assert jack_tokenizer.cur_line == "\n"
        # NOTE: We must manually advance twice
        #       The first time since we've eaten *\
        #       The second time since we're at a blank new line
        jack_tokenizer.cur_line = jack_tokenizer.file.readline()
        jack_tokenizer.cur_line = jack_tokenizer.file.readline()

        assert jack_tokenizer.cur_line == "/** Followed by a docstring */\n"
        assert jack_tokenizer.next_is_comment()
        assert jack_tokenizer.cur_line == "\n"
        assert not jack_tokenizer.next_is_comment()
        # NOTE: We must manually advance since we are at a newline
        jack_tokenizer.cur_line = jack_tokenizer.file.readline()

        assert jack_tokenizer.cur_line == "class Comments {\n"
        jack_tokenizer.cur_line = jack_tokenizer.file.readline()
        assert jack_tokenizer.cur_line == "  // Which has some static variables\n"
        assert jack_tokenizer.next_is_comment()

        assert (
            jack_tokenizer.cur_line
            == "  static int dummy;  // Which has a line comment\n"
        )
        assert not jack_tokenizer.next_is_comment()
        jack_tokenizer.eat(jack_tokenizer.cur_line.find(";") + 1)
        assert jack_tokenizer.cur_line == "  // Which has a line comment\n"
        assert jack_tokenizer.next_is_comment()

        assert (
            jack_tokenizer.cur_line
            == "  static int dummy2;  /* Which has a block comment **/\n"
        )
        assert not jack_tokenizer.next_is_comment()
        jack_tokenizer.eat(jack_tokenizer.cur_line.find(";") + 1)
        assert jack_tokenizer.next_is_comment()
        # NOTE: The cur line will be the leftover when */ is eaten
        assert jack_tokenizer.cur_line == "\n"
        assert not jack_tokenizer.next_is_comment()
        jack_tokenizer.cur_line = jack_tokenizer.file.readline()

        assert jack_tokenizer.cur_line == "  static int dummy3;  /*\n"
        assert not jack_tokenizer.next_is_comment()
        jack_tokenizer.eat(jack_tokenizer.cur_line.find(";") + 1)
        assert jack_tokenizer.next_is_comment()
        # NOTE: The cur line will be the leftover when */ is eaten
        assert jack_tokenizer.cur_line == "\n"
        assert not jack_tokenizer.next_is_comment()
        jack_tokenizer.cur_line = jack_tokenizer.file.readline()

        assert (
            jack_tokenizer.cur_line
            == "  static int /* even inline comments */ dummy4;\n"
        )
        assert not jack_tokenizer.next_is_comment()
        before_comment = "int"
        jack_tokenizer.eat(
            jack_tokenizer.cur_line.find(before_comment) + len(before_comment)
        )
        assert jack_tokenizer.cur_line == " /* even inline comments */ dummy4;\n"
        assert jack_tokenizer.next_is_comment()
        assert jack_tokenizer.cur_line == " dummy4;\n"
        assert not jack_tokenizer.next_is_comment()
        jack_tokenizer.cur_line = jack_tokenizer.file.readline()

        assert jack_tokenizer.cur_line == "\n"
        assert not jack_tokenizer.next_is_comment()
        jack_tokenizer.cur_line = jack_tokenizer.file.readline()

        assert jack_tokenizer.cur_line == "  function void noFunc(){ return; }\n"
        assert not jack_tokenizer.next_is_comment()
        jack_tokenizer.cur_line = jack_tokenizer.file.readline()

        assert jack_tokenizer.cur_line == "}\n"
        assert not jack_tokenizer.next_is_comment()
