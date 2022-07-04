"""Module containing the JackTokenizer class."""

import re
from io import TextIOWrapper
from typing import Literal, get_args

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
        self.token_match = ""
        self.cur_token = ""
        self.cur_line = self.file.readline()

        keywords = tuple(kw.lower() for kw in get_args(KEYWORD))
        symbols = tuple(kw for kw in get_args(SYMBOL))

        keywords_regex_str = "|".join(keywords)
        # NOTE: Ned dummy {''} to join with backslash as this is an escape character
        symbols_regex_str = rf"{'|'}\{''}".join(symbols)
        integer_constant_regex_str = r"\d{1,5}"
        string_constant_regex_str = r"\"\w+\""
        identifier_regex_str = r"\w+"
        self.line_comment_regex = re.compile(r"\s*//")
        self.block_comment_start_regex = re.compile(r"\s*/\*")
        self.block_comment_end_regex = re.compile(r"\s*\*/")
        self.compiled_regexes = {
            "all": re.compile(
                rf"\s*{keywords_regex_str}|"
                rf"\{''}{symbols_regex_str}|"
                f"{integer_constant_regex_str}|"
                f"{string_constant_regex_str}|"
                f"{identifier_regex_str}"
            ),
            "keywords": re.compile(keywords_regex_str),
            "symbols": re.compile(symbols_regex_str),
            "integer_constant": re.compile(integer_constant_regex_str),
            "string_constant": re.compile(string_constant_regex_str),
            "identifier": re.compile(identifier_regex_str),
        }

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
            if self._next_is_comment():
                continue

            self.token_match = self.compiled_regexes["all"].match(self.cur_line)
            if self.token_match is not None:
                found_token = True
                break
            self.cur_line = self.file.readline()

        self.file.seek(cur_pos)
        # Next line is empty, no more tokens
        return found_token

    def _next_is_comment(self) -> bool:
        """
        Check if the next part of the current line is a comment, advance the line.

        Returns:
            bool: True
        """
        # Check for line commands
        line_comment_match = self.line_comment_regex.match(self.cur_line)
        if line_comment_match is not None:
            self.cur_line = self.file.readline()
            return True

        # Check for block commands
        block_comment_start_match = self.block_comment_start_regex.match(self.cur_line)
        if block_comment_start_match is not None:
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

        Will populate self.current_token, and skip over whitespace and comments.
        If it reaches the end of the tokens, self.current_token will be set to "".

        This method should be called only if has_more_lines is true.
        """
        # NOTE: group(1) is the first group matched
        self.cur_token = self.token_match.group(1).replace(" ", "")
        self._eat(self.cur_token)

    def token_type(self) -> TOKEN:
        """Return the current token type.

        This method should only be called if `has_more_tokens` is True

        Returns:
            TOKEN: The token type
        """
        if self.compiled_regexes["keywords"].match(self.cur_line) is not None:
            return "KEYWORD"
        elif self.compiled_regexes["symbols"].match(self.cur_line) is not None:
            return "SYMBOL"
        elif self.compiled_regexes["identifier"].match(self.cur_line) is not None:
            return "IDENTIFIER"
        elif self.compiled_regexes["integer_constant"].match(self.cur_line) is not None:
            return "INT_CONST"
        elif self.compiled_regexes["string_constant"].match(self.cur_line) is not None:
            return "STRING_CONST"

    def keyword(self) -> KEYWORD:
        """Return the keyword which is the current token.

        This method should be called only if `tokenType` is `KEYWORD`

        Returns:
            KEYWORD: The keyword
        """
        return self.cur_token

    def symbol(self) -> SYMBOL:
        """Return the character which is the current token.

        This method should be called only if `tokenType` is `SYMBOL`

        Returns:
            SYMBOL: The symbol
        """
        return self.cur_token

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
        return self.cur_token

    def string_val(self) -> str:
        """Return the string value which is the current token.

        The string value will be stripped of the enclosing double quotes

        This method should be called only if `tokenType` is `STRING_CONST`

        Returns:
            str: The string
        """
        return self.cur_token
