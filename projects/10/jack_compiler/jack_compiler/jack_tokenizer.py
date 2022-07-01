"""Module containing the JackTokenizer class."""

from typing import Literal

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

    def __init__(self, path: str) -> None:
        """Open input file to parse.

        Args:
            path (str): Path to file to parse
        """

    def __del__(self):
        """Close the file."""

    def has_more_tokens(self) -> bool:
        """Return if the file has more tokens.

        Returns:
            bool: True if the file has more tokens
        """

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
