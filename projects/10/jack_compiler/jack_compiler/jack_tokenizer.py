"""Module containing the JackTokenizer class."""

import re
from io import TextIOWrapper
from typing import Literal, Optional, get_args

TOKEN = Literal[
    "KEYWORD",
    "SYMBOL",
    "IDENTIFIER",
    "INT_CONST",
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
        self.match: Optional[re.Match[str]] = None
        self.cur_token = ""
        self.cur_line = self.file.readline()

        keywords = tuple(kw.lower() for kw in get_args(KEYWORD))
        symbols = tuple(kw for kw in get_args(SYMBOL))

        backslash = "\\"  # f-string expression part cannot include a backslash
        # As we do greedy capture, we must have the comment first in order not
        # to classify as a SYMBOL
        regex_str = (
            r"\s*(?P<LINE_COMMENT>//)|"
            r"\s*(?P<BLOCK_COMMENT_START>/\*)|"
            f"\s*(?P<KEYWORD>{'|'.join(keywords)})|"
            rf"\s*(?P<SYMBOL>{backslash}{f'|{backslash}'.join(symbols)})|"
            r"\s*(?P<INT_CONST>\d{1,5})|"
            r"\s*(?P<STR_CONST>\"\w+\")|"
            r"\s*(?P<IDENTIFIER>\w+)"
        )
        self.compiled_regex = re.compile(regex_str)
        self.block_comment_end_regex = re.compile(r"\s*\*/")

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
        while bool(self.cur_line):
            self.match = self.compiled_regex.match(self.cur_line)

            # On newlines there will be no match
            if self.match is None:
                self.cur_line = self.file.readline()
                continue

            if self._next_is_comment():
                continue

            # Since we have a match we can read the current token
            # NOTE: match[0] is the first group matched
            self.token_match = self.match[0]
            found_token = True
            break

        self.file.seek(cur_pos)
        # Next line is empty, no more tokens
        return found_token

    def _next_is_comment(self) -> bool:
        """
        Check if the next part of the current line is a comment, advance the line.

        Returns:
            bool: True
        """
        if self.match is None:
            return False

        # Check for line commands
        if self.match.lastgroup == "LINE_COMMENT":
            self.cur_line = self.file.readline()
            return True

        # Check for block commands
        if self.match.lastgroup == "BLOCK_COMMENT_START":
            # Advance until */
            found_end = False
            while not found_end:
                # NOTE: We search as the */ may not be in the start
                block_comment_end_match = self.block_comment_end_regex.search(
                    self.cur_line
                )
                if block_comment_end_match is not None:
                    found_end = True
                    # NOTE: span() returns the (match.start(group), match.end(group))
                    self._eat(block_comment_end_match.span()[1])
                else:
                    self.cur_line = self.file.readline()
            return True

        return False

    def _eat(self, char_number: int) -> None:
        """Eat the first characters of the current line.

        Args:
            char_number (int): Number of characters to eat
        """
        self.cur_line = self.cur_line[char_number:]

    def advance(self) -> None:
        """Read the next token and make it the current token.

        Will populate self.cur_token, and skip over whitespace and comments.
        If it reaches the end of the tokens, self.current_token will be set to "".

        This method should be called only if has_more_lines is true.
        """
        if self.match is None:
            raise RuntimeError("Could not set cur_token as no matches were found")
        self.cur_token = self.match[0]
        self._eat(len(self.cur_token))

    def token_type(self) -> TOKEN:
        """Return the current token type.

        This method should only be called if `has_more_tokens` is True

        Returns:
            TOKEN: The token type
        """
        if self.match is None:
            raise RuntimeError("No match found")
        if self.match.lastgroup not in get_args(TOKEN):
            raise RuntimeError(f"{self.match.lastgroup} not in {get_args(TOKEN)}")
        # We're checking if self.match.lastgroup is in TOKEN
        # hence we ignore mypy error
        return self.match.lastgroup  # type: ignore

    def keyword(self) -> KEYWORD:
        """Return the keyword which is the current token.

        This method should be called only if `tokenType` is `KEYWORD`

        Returns:
            KEYWORD: The keyword
        """
        if self.match is None:
            raise RuntimeError("No match found")
        if self.match.lastgroup not in get_args(KEYWORD):
            raise RuntimeError(f"{self.cur_line} not in {get_args(KEYWORD)}")
        # We're checking if self.match.lastgroup is in KEYWORD
        # hence we ignore mypy error
        return self.cur_token  # type: ignore

    def symbol(self) -> SYMBOL:
        """Return the character which is the current token.

        This method should be called only if `tokenType` is `SYMBOL`

        Returns:
            SYMBOL: The symbol
        """
        if self.match is None:
            raise RuntimeError("No match found")
        if self.match.lastgroup not in get_args(SYMBOL):
            raise RuntimeError(f"{self.cur_line} not in {get_args(SYMBOL)}")
        # We're checking if self.match.lastgroup is in SYMBOL
        # hence we ignore mypy error
        return self.cur_token  # type: ignore

    def identifier(self) -> str:
        """Return the identifier which is the current token.

        This method should be called only if `tokenType` is `IDENTIFIER`

        Returns:
            str: The identifier
        """
        return self.cur_token

    def int_val(self) -> int:
        """Return the integer value which is the current token.

        This method should be called only if `tokenType` is `INT_CONST`

        Returns:
            int: The integer
        """
        return int(self.cur_token)

    def string_val(self) -> str:
        """Return the string value which is the current token.

        The string value will be stripped of the enclosing double quotes

        This method should be called only if `tokenType` is `STRING_CONST`

        Returns:
            str: The string
        """
        return self.cur_token
