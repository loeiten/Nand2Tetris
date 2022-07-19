"""Module containing the CompilationEngine class."""

from io import TextIOWrapper
from typing import Literal

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

    def __init__(self, in_file: TextIOWrapper, out_file: TextIOWrapper) -> None:
        """Create a new compilation engine with the given input and output.

        Args:
            in_file (TextIOWrapper): Path of the input file
            out_file (TextIOWrapper): Path of the output file
        """
        self.in_file = in_file
        self.out_file = out_file
        self.indentation = 0

    def write_token(self, token_type: TerminalElement, token: str) -> None:
        """Write the token or grammar wrapped by the xml type to the out_file.

        Args:
            token_type (TERMINAL_ELEMENT): The type to use as a tag
            token (str): The body inside the tag.
                <, >, ", and & are outputted as &lt;, &gt;, &quot;, and &amp;
        """
        if token == "<":
            token = "&lt;"
        if token == ">":
            token = "&gt;"
        if token == '"':
            token = "&quot;"
        if token == "&":
            token = "&amp;"
        self.out_file.write(
            f"{' '*self.indentation}<{token_type}> {token} </{token_type}>\n"
        )

    def open_grammar(self, grammar_type: NonTerminalElement) -> None:
        """Open a grammar body.

        Args:
            grammar_type (NON_TERMINAL_ELEMENT): The grammar tag
        """
        self.out_file.write(f"{' '*self.indentation}<{grammar_type}>")
        # Increase the current indentation
        self.indentation += 2

    def close_grammar(self, grammar_type: NonTerminalElement) -> None:
        """Close the grammar body.

        Args:
            grammar_type (NON_TERMINAL_ELEMENT): The grammar tag
        """
        # Decrease the current indentation
        self.indentation = max(0, self.indentation - 2)
        self.out_file.write(f"{' '*self.indentation}</{grammar_type}>")

    def compile_class(self) -> None:
        """Compile a complete class."""

    def compile_class_var_dec(self) -> None:
        """Compile a static variable declaration or a field variable declaration."""

    def compile_subroutine_dec(self) -> None:
        """Compile a complete method, function or constructor."""

    def compile_parameter_list(self) -> None:
        """
        Compile a (possibly empty) parameter list.

        Does not handle the enclosing "()"
        """

    def compile_subroutine_body(self) -> None:
        """Compile a subroutine's body."""

    def compile_var_dec(self) -> None:
        """Compile a var declaration."""

    def compile_statements(self) -> None:
        """
        Compile a sequence of statements.

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
