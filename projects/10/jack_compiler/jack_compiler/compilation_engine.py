"""Module containing the CompilationEngine class."""

from io import TextIOWrapper
from typing import Literal

from jack_compiler.jack_tokenizer import JackTokenizer

TerminalElement = Literal[
    "keyword", "symbol", "integerConstant", "stringConstant", "identifier"
]

NonTerminalElement = Literal[
    "class",
    "classVarDec",
    "subroutineDec",
    "parameterList",
    "subroutineBody",
    "varDec",
    "statements",
    "LetStatement",
    "ifStatement",
    "whileStatement",
    "doStatement",
    "returnStatement",
    "expression",
    "term",
    "expressionList",
]


class CompilationEngine:
    """Class which generates the compiler's output."""

    token_map = {
        "KEYWORD": {"text": "keyword", "function_name": "keyword"},
        "SYMBOL": {"text": "symbol", "function_name": "symbol"},
        "IDENTIFIER": {"text": "identifier", "function_name": "identifier"},
        "INT_CONST": {"text": "integerConstant", "function_name": "int_val"},
        "STRING_CONST": {"text": "stringConstant", "function_name": "string_val"},
    }

    def __init__(self, jack_tokenizer: JackTokenizer, out_file: TextIOWrapper) -> None:
        """Create a new compilation engine with the given input and output.

        Args:
            jack_tokenizer (JackTokenizer): The tokenizer
            out_file (TextIOWrapper): Path of the output file

        Raises:
            RuntimeError: If the file does not contain any tokens
        """
        self.jack_tokenizer = jack_tokenizer
        self.out_file = out_file
        self.indentation = 0

        self.token_type = ""
        self.token = ""

        if not jack_tokenizer.has_more_tokens():
            raise RuntimeError(
                f"Running tokenizer on empty file {jack_tokenizer.file.name}"
            )
        # Above we use the file to check whether we have more tokens
        # This alters the file pointer of the file
        # Hence we must reset the pointer:
        self.jack_tokenizer.reset()

    def _advance(self) -> None:
        """Advance the tokenizer."""
        self.jack_tokenizer.advance()

        token_type = self.jack_tokenizer.token_type()
        func = getattr(self.jack_tokenizer, self.token_map[token_type]["function_name"])
        self.token = func()
        self.token_type = self.token_map[token_type]["text"]
        if token_type == "KEYWORD":
            self.token = self.token.lower()

    def compile_tokens_only(self) -> None:
        """Only compile tokens."""
        while self.jack_tokenizer.has_more_tokens():
            self._advance()
            # Type ignore as mypy doesn't detect that we are ensuring the
            # correct input type for token_type
            self.write_token(
                token_type=self.token_type, token=self.token  # type: ignore
            )

    def write_token(self, token_type: TerminalElement, token: str) -> None:
        """Write the token or grammar wrapped by the xml type to the out_file.

        Args:
            token_type (TERMINAL_ELEMENT): The type to use as a tag
            token (str): The body inside the tag.
                <, >, ", and & are outputted as &lt;, &gt;, &quot;, and &amp;
        """
        if token == "<":
            token = "&lt;"
        elif token == ">":
            token = "&gt;"
        elif token == '"':
            token = "&quot;"
        elif token == "&":
            token = "&amp;"
        self.out_file.write(
            f"{' '*self.indentation}<{token_type}> {token} </{token_type}>\n"
        )

    def open_grammar(self, grammar_type: NonTerminalElement) -> None:
        """Open a grammar body.

        Args:
            grammar_type (NON_TERMINAL_ELEMENT): The grammar tag
        """
        self.out_file.write(f"{' '*self.indentation}<{grammar_type}>\n")
        # Increase the current indentation
        self.indentation += 2

    def close_grammar(self, grammar_type: NonTerminalElement) -> None:
        """Close the grammar body.

        Args:
            grammar_type (NON_TERMINAL_ELEMENT): The grammar tag
        """
        # Decrease the current indentation
        self.indentation = max(0, self.indentation - 2)
        self.out_file.write(f"{' '*self.indentation}</{grammar_type}>\n")

    def compile_class(self) -> None:
        """Compile a complete class."""
        assert self.jack_tokenizer.has_more_tokens()
        self._advance()
        if self.token != "class":
            raise RuntimeError(
                f"{self.jack_tokenizer.file.name} did not start with a definition of 'class'"
            )
        # Write class
        self.open_grammar("class")
        # Type ignore as mypy doesn't detect that we are ensuring the
        # correct input type for token_type
        self.write_token(self.token_type, self.token)  # type: ignore

        # Class name
        assert self.jack_tokenizer.has_more_tokens()
        self._advance()
        self.write_token(self.token_type, self.token)  # type: ignore

        # The { symbol
        assert self.jack_tokenizer.has_more_tokens()
        self._advance()
        self.write_token(self.token_type, self.token)  # type: ignore

        # Zero or more classVarDec
        assert self.jack_tokenizer.has_more_tokens()
        self._advance()
        while self.token in ("static", "field"):
            self.compile_class_var_dec()
            assert self.jack_tokenizer.has_more_tokens()
            self._advance()

        # Zero or more subroutineDec
        assert self.jack_tokenizer.has_more_tokens()
        self._advance()
        while self.token in ("constructor", "function", "method"):
            self.compile_subroutine_dec()
            assert self.jack_tokenizer.has_more_tokens()
            self._advance()

        self.close_grammar("class")

    def compile_class_var_dec(self) -> None:
        """Compile a static variable declaration or a field variable declaration."""
        self.open_grammar("classVarDec")

        # static | field
        self.write_token(self.token_type, self.token)  # type: ignore

        # type
        assert self.jack_tokenizer.has_more_tokens()
        self._advance()
        self.write_token(self.token_type, self.token)  # type: ignore

        # varName
        assert self.jack_tokenizer.has_more_tokens()
        self._advance()
        self.write_token(self.token_type, self.token)  # type: ignore

        assert self.jack_tokenizer.has_more_tokens()
        self._advance()

        # (, varName)*
        while self.token == ",":
            # The , symbol
            self.write_token(self.token_type, self.token)  # type: ignore

            # varName
            assert self.jack_tokenizer.has_more_tokens()
            self._advance()
            self.write_token(self.token_type, self.token)  # type: ignore

            assert self.jack_tokenizer.has_more_tokens()
            self._advance()

        # The ; symbol
        self.write_token(self.token_type, self.token)  # type: ignore

        self.close_grammar("classVarDec")

    def compile_subroutine_dec(self) -> None:
        """Compile a complete method, function or constructor."""
        self.open_grammar("subroutineDec")

        # constructor | function | method
        self.write_token(self.token_type, self.token)  # type: ignore

        # void | type
        assert self.jack_tokenizer.has_more_tokens()
        self._advance()
        self.write_token(self.token_type, self.token)  # type: ignore

        # subroutineName
        assert self.jack_tokenizer.has_more_tokens()
        self._advance()
        self.write_token(self.token_type, self.token)  # type: ignore

        # The ( symbol
        assert self.jack_tokenizer.has_more_tokens()
        self._advance()
        self.write_token(self.token_type, self.token)  # type: ignore

        assert self.jack_tokenizer.has_more_tokens()
        self._advance()

        # parameterList
        self.compile_parameter_list()

        # The ) symbol
        self.write_token(self.token_type, self.token)  # type: ignore

        assert self.jack_tokenizer.has_more_tokens()
        self._advance()

        # subRoutine body
        self.compile_subroutine_body()

        self.close_grammar("subroutineDec")

    def compile_parameter_list(self) -> None:
        """Compile a (possibly empty) parameter list.

        Does not handle the enclosing "()"
        """
        self.open_grammar("parameterList")

        while self.token != ")":
            # type | varName | the symbol ,
            self.write_token(self.token_type, self.token)  # type: ignore
            assert self.jack_tokenizer.has_more_tokens()
            self._advance()

        self.close_grammar("parameterList")

    def compile_subroutine_body(self) -> None:
        """Compile a subroutine's body."""
        self.open_grammar("subroutineBody")

        # The { symbol
        self.write_token(self.token_type, self.token)  # type: ignore

        assert self.jack_tokenizer.has_more_tokens()
        self._advance()

        # varDec
        while self.token == "var":
            self.compile_var_dec()

        # The } symbol
        self.write_token(self.token_type, self.token)  # type: ignore

        self.close_grammar("subroutineBody")

    def compile_var_dec(self) -> None:
        """Compile a var declaration."""
        self.open_grammar("varDec")

        # var
        self.write_token(self.token_type, self.token)  # type: ignore

        self.close_grammar("varDec")

    def compile_statements(self) -> None:
        """Compile a sequence of statements.

        Does not handle the enclosing "{}"
        """

    def compile_let(self) -> None:
        """Compile a `let` statement."""

    def compile_if(self) -> None:
        """Compile an `if` statement, possibly with a trailing else clause."""

    def compile_while(self) -> None:
        """Compile a `while` statement."""

    def compile_do(self) -> None:
        """Compile a `do` statement."""

    def compile_return(self) -> None:
        """Compile a `return` statement."""

    def compile_expression(self) -> None:
        """Compile an `expression` statement."""

    def compile_term(self) -> None:
        """Compile a term.

        If the current token is an `IDENTIFIER`, the routine distinguishes
        between a variable, an array entry, or a subroutine call.
        A single look-ahead token, which may be one of `[`, `(`, or `.` is used
        to distinguish between the possibilities.
        Any other token is not part of this term will not be advanced over.
        """

    def compile_expression_list(self) -> None:
        """Compile a (possibly empty) comma-separated list of expressions."""
