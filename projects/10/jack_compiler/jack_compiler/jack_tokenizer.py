"""Module containing the JackTokenizer class."""

import re
from io import TextIOWrapper
from typing import Literal, get_args

TOKEN = Literal[
    "KEYWORD",
    "SYMBOL",
    "IDENTIFIER",
    "INT_CONT",
    "STRING_CONST",
]

KEYWORD = Literal[
    "CLASS",
    "METHOD",
    "FUNCTION",
    "CONSTRUCTOR",
    "INT",
    "BOOLEAN",
    "CHAR",
    "VOID",
    "VAR",
    "STATIC",
    "FIELD",
    "LET",
    "DO",
    "IF",
    "ELSE",
    "WHILE",
    "RETURN",
    "TRUE",
    "FALSE",
    "NULL",
    "THIS",
]

SYMBOL = Literal[
    "{",
    "}",
    "(",
    ")",
    "[",
    "]",
    ".",
    ",",
    ";",
    "+",
    "-",
    "*",
    "/",
    "&",
    "|",
    "<",
    ">",
    "=",
    "~",
]


class JackTokenizer:
    """Class tokenizing .jack files."""

    def __init__(self, in_file: TextIOWrapper) -> None:
        """Prepare to parse input stream.

        Args:
            in_file (TextIOWrapper): File to parse
        """
        self.file = in_file
        keywords = tuple(kw.lower() for kw in get_args(KEYWORD))
        symbols = tuple(kw for kw in get_args(SYMBOL))

        keywords_regex_str = "|".join(keywords)
        symbols_regex_str = r"\\".join(symbols)
        integer_constant_regex_str = r"\d{1,5}"
        string_constant_regex_str = r"\"\w?\""
        self.token_regex = re.compile(
            rf"\s*{keywords_regex_str}|"
            rf"{symbols_regex_str}|"
            rf"{integer_constant_regex_str}|"
            rf"{string_constant_regex_str}"
        )

    def has_more_tokens(self) -> bool:
        """Return if the file has more tokens.

        Returns:
            bool: True if the file has more tokens
        """
        found_token = False
        cur_pos = self.file.tell()
        # The return value of .readline() is unambiguous
        # It will return "" only on the last line
        # A blank line will be returned as "\n"
        cur_line = self.file.readline()
        while bool(cur_line):
            if self.token_regex.match(cur_line) is not None:
                found_token = True
                break
            cur_line = self.file.readline()

        self.file.seek(cur_pos)
        # Next line is empty, no more tokens
        return found_token

    def advance(self) -> None:
        """Read the next token and make it the current token.

        Will populate self.current_token, and skip over whitespace and comments.
        If it reaches the end of the tokens, self.current_token will be set to "".

        This method should be called only if has_more_lines is true.
        """

    def token_type(self) -> TOKEN:
        """Return the current token type.

        This method should only be called if `has_more_tokens` is True

        Returns:
            TOKEN: The token type
        """

    def keyword(self) -> KEYWORD:
        """Return the keyword which is the current token.

        This method should be called only if `tokenType` is `KEYWORD`

        Returns:
            KEYWORD: The keyword
        """

    def symbol(self) -> SYMBOL:
        """Return the character which is the current token.

        This method should be called only if `tokenType` is `SYMBOL`

        Returns:
            SYMBOL: The symbol
        """

    def identifier(self) -> str:
        """Return the identifier which is the current token.

        This method should be called only if `tokenType` is `IDENTIFIER`

        Returns:
            str: The identifier
        """

    def int_val(self) -> int:
        """Return the integer value which is the current token.

        This method should be called only if `tokenType` is `INT_CONST`

        Returns:
            int: The integer
        """

    def string_val(self) -> str:
        """Return the string value which is the current token.

        The string value will be stripped of the enclosing double quotes

        This method should be called only if `tokenType` is `STRING_CONST`

        Returns:
            str: The string
        """
