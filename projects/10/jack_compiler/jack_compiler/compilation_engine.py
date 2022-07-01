"""Module containing the CompilationEngine class."""

from io import TextIOWrapper


class CompilationEngine:
    """Class which generates the compiler's output."""

    def __init__(self, in_file: TextIOWrapper, out_file: TextIOWrapper) -> None:
        """Create a new compilation engine with the given input and output.

        Args:
            in_path (Path): Path of the input file
            out_path (Path): Path of the output file
        """

    def __del__(self) -> None:
        """Close the files."""

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
