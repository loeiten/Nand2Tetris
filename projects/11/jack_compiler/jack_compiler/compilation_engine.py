"""Module containing the CompilationEngine class."""

from io import TextIOWrapper
from typing import Literal, Union, get_args

from jack_compiler.jack_tokenizer import JackTokenizer
from jack_compiler.symbol_table import SymbolTable

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
    "letStatement",
    "ifStatement",
    "whileStatement",
    "doStatement",
    "returnStatement",
    "expression",
    "term",
    "expressionList",
]

Op = Literal["+", "-", "*", "/", "&", "|", "<", ">", "="]


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

        self.class_table = SymbolTable()
        self.subroutine_table = SymbolTable()

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
            self._write_token(
                token_type=self.token_type, token=self.token  # type: ignore
            )

    def _write_token(
        self, token_type: TerminalElement, token: Union[str, int], definition=False
    ) -> None:
        """Write the token or grammar wrapped by the xml type to the out_file.

        Args:
            token_type (TERMINAL_ELEMENT): The type to use as a tag
            token (Union[str, int]): The body inside the tag.
                <, >, ", and & are outputted as &lt;, &gt;, &quot;, and &amp;
            definition (bool): Whether an identifier is being defined or used
        """
        token_str = str(token)
        # If the type is identifier, we need to distinguish between
        # 1. The category (var, arg, static, field, class, subroutine)
        # 2. If category not in (class, subroutine): The running index
        # 3. If the identifier is being defined or used
        if token_type == "identifier":
            # First we figure out where our symbol is (if in any)
            # Search first in the subroutine table
            kind = self.subroutine_table.kind_of(token_str)
            table = self.subroutine_table
            if kind is None:
                # Search then in the class table
                kind = self.class_table.kind_of(token_str)
                table = self.class_table
            if kind is None:
                # We must be dealing with either a class or a subroutine
                # If it is a subroutine name it must be followed by a "("
                class_or_subroutine = (
                    "subroutine" if self.jack_tokenizer.look_ahead() == "(" else "class"
                )
                cur_token_type = (
                    f"{class_or_subroutine}_{'definition' if definition else 'usage'}"
                )
            else:
                index = table.index_of(token_str)
                cur_token_type = (
                    f"{kind}_{index}_{'definition' if definition else 'usage'}"
                )
        else:
            cur_token_type = token_type
        token = (
            token_str.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
        )
        self.out_file.write(
            f"{' '*self.indentation}<{cur_token_type}> {token} </{cur_token_type}>\n"
        )

    def _open_grammar(self, grammar_type: NonTerminalElement) -> None:
        """Open a grammar body.

        Args:
            grammar_type (NON_TERMINAL_ELEMENT): The grammar tag
        """
        self.out_file.write(f"{' '*self.indentation}<{grammar_type}>\n")
        # Increase the current indentation
        self.indentation += 2

    def _close_grammar(self, grammar_type: NonTerminalElement) -> None:
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
        self._open_grammar("class")
        # Type ignore as mypy doesn't detect that we are ensuring the
        # correct input type for token_type
        self._write_token(self.token_type, self.token)  # type: ignore

        # Class name
        assert self.jack_tokenizer.has_more_tokens()
        self._advance()
        self._write_token(self.token_type, self.token)  # type: ignore

        # The { symbol
        assert self.jack_tokenizer.has_more_tokens()
        self._advance()
        self._write_token(self.token_type, self.token)  # type: ignore

        # Zero or more classVarDec
        next_token = self.jack_tokenizer.look_ahead()
        while next_token in ("static", "field"):
            assert self.jack_tokenizer.has_more_tokens()
            self._advance()
            self.compile_class_var_dec()
            next_token = self.jack_tokenizer.look_ahead()

        # Zero or more subroutineDec
        next_token = self.jack_tokenizer.look_ahead()
        while next_token in ("constructor", "function", "method"):
            assert self.jack_tokenizer.has_more_tokens()
            self._advance()
            self.compile_subroutine_dec()
            next_token = self.jack_tokenizer.look_ahead()

        # The } symbol
        assert self.jack_tokenizer.has_more_tokens()
        self._advance()
        self._write_token(self.token_type, self.token)  # type: ignore

        self._close_grammar("class")

    def compile_class_var_dec(self) -> None:
        """Compile a static variable declaration or a field variable declaration."""
        self._open_grammar("classVarDec")

        # static | field
        self._write_token(self.token_type, self.token)  # type: ignore

        # type
        assert self.jack_tokenizer.has_more_tokens()
        self._advance()
        # We may be dealing with a class, which in this case is being used
        if self.token_type == "identifier":
            self._write_token(self.token_type, self.token, definition=False)  # type: ignore

        # varName
        assert self.jack_tokenizer.has_more_tokens()
        self._advance()
        # Here the variables are being defined
        self._write_token(self.token_type, self.token, definition=True)  # type: ignore

        assert self.jack_tokenizer.has_more_tokens()
        self._advance()

        # (, varName)*
        while self.token == ",":
            # The , symbol
            self._write_token(self.token_type, self.token)  # type: ignore

            # varName
            assert self.jack_tokenizer.has_more_tokens()
            self._advance()
            # Here the variables are being defined
            self._write_token(self.token_type, self.token, definition=True)  # type: ignore

            assert self.jack_tokenizer.has_more_tokens()
            self._advance()

        # The ; symbol
        self._write_token(self.token_type, self.token)  # type: ignore

        self._close_grammar("classVarDec")

    def compile_subroutine_dec(self) -> None:
        """Compile a complete method, function or constructor."""
        self._open_grammar("subroutineDec")

        # constructor | function | method
        self._write_token(self.token_type, self.token)  # type: ignore

        # void | type
        assert self.jack_tokenizer.has_more_tokens()
        self._advance()
        self._write_token(self.token_type, self.token)  # type: ignore

        # subroutineName
        assert self.jack_tokenizer.has_more_tokens()
        self._advance()
        self._write_token(self.token_type, self.token)  # type: ignore

        # The ( symbol
        assert self.jack_tokenizer.has_more_tokens()
        self._advance()
        self._write_token(self.token_type, self.token)  # type: ignore

        # parameterList
        next_token = self.jack_tokenizer.look_ahead()
        if next_token != ")":
            assert self.jack_tokenizer.has_more_tokens()
            self._advance()
            self.compile_parameter_list()
        else:
            self._open_grammar("parameterList")
            self._close_grammar("parameterList")

        # The ) symbol
        assert self.jack_tokenizer.has_more_tokens()
        self._advance()
        self._write_token(self.token_type, self.token)  # type: ignore

        # subRoutine body
        assert self.jack_tokenizer.has_more_tokens()
        self._advance()
        self.compile_subroutine_body()

        self._close_grammar("subroutineDec")

        # Reset the subroutine_table
        self.subroutine_table = SymbolTable()

    def compile_parameter_list(self) -> None:
        """Compile a (possibly empty) parameter list.

        Does not handle the enclosing "()"
        """
        self._open_grammar("parameterList")

        next_token = self.jack_tokenizer.look_ahead()
        if next_token != ")":
            # type
            self._write_token(self.token_type, self.token)  # type: ignore

            # varName
            assert self.jack_tokenizer.has_more_tokens()
            self._advance()
            # Here the variables are being defined
            self._write_token(self.token_type, self.token, definition=True)  # type: ignore

            next_token = self.jack_tokenizer.look_ahead()
            while next_token == ",":
                # ,
                assert self.jack_tokenizer.has_more_tokens()
                self._advance()
                self._write_token(self.token_type, self.token)  # type: ignore

                # type
                assert self.jack_tokenizer.has_more_tokens()
                self._advance()
                self._write_token(self.token_type, self.token)  # type: ignore

                # varName
                assert self.jack_tokenizer.has_more_tokens()
                self._advance()
                # Here the variables are being defined
                self._write_token(self.token_type, self.token, definition=True)  # type: ignore

                next_token = self.jack_tokenizer.look_ahead()

        self._close_grammar("parameterList")

    def compile_subroutine_body(self) -> None:
        """Compile a subroutine's body."""
        self._open_grammar("subroutineBody")

        # The { symbol
        self._write_token(self.token_type, self.token)  # type: ignore

        # varDec
        next_token = self.jack_tokenizer.look_ahead()
        while next_token == "var":
            assert self.jack_tokenizer.has_more_tokens()
            self._advance()
            self.compile_var_dec()
            next_token = self.jack_tokenizer.look_ahead()

        # statements
        next_token = self.jack_tokenizer.look_ahead()
        if next_token != "}":
            assert self.jack_tokenizer.has_more_tokens()
            self._advance()
            self.compile_statements()

        # The } symbol
        assert self.jack_tokenizer.has_more_tokens()
        self._advance()
        self._write_token(self.token_type, self.token)  # type: ignore

        self._close_grammar("subroutineBody")

    def compile_var_dec(self) -> None:
        """Compile a var declaration."""
        self._open_grammar("varDec")

        # var
        self._write_token(self.token_type, self.token)  # type: ignore

        # type
        assert self.jack_tokenizer.has_more_tokens()
        self._advance()
        self._write_token(self.token_type, self.token)  # type: ignore

        # varName
        assert self.jack_tokenizer.has_more_tokens()
        self._advance()
        # Here the tokens are being defined
        self._write_token(self.token_type, self.token, definition=True)  # type: ignore

        # (, varName)*
        next_token = self.jack_tokenizer.look_ahead()
        while next_token == ",":
            # The , symbol
            assert self.jack_tokenizer.has_more_tokens()
            self._advance()
            self._write_token(self.token_type, self.token)  # type: ignore

            # varName
            assert self.jack_tokenizer.has_more_tokens()
            self._advance()
            # Here the tokens are being defined
            self._write_token(self.token_type, self.token, definition=True)  # type: ignore

            next_token = self.jack_tokenizer.look_ahead()

        # The symbol ;
        assert self.jack_tokenizer.has_more_tokens()
        self._advance()
        self._write_token(self.token_type, self.token)  # type: ignore

        self._close_grammar("varDec")

    def compile_statements(self) -> None:
        """Compile a sequence of statements.

        Does not handle the enclosing "{}"
        """
        self._open_grammar("statements")

        while self.token in ("let", "if", "while", "do", "return"):
            if self.token == "let":
                self.compile_let()
            elif self.token == "if":
                self.compile_if()
            elif self.token == "while":
                self.compile_while()
            elif self.token == "do":
                self.compile_do()
            elif self.token == "return":
                self.compile_return()
            next_token = self.jack_tokenizer.look_ahead()
            if next_token in ("let", "if", "while", "do", "return"):
                assert self.jack_tokenizer.has_more_tokens()
                self._advance()

        self._close_grammar("statements")

    def compile_let(self) -> None:
        """Compile a `let` statement."""
        self._open_grammar("letStatement")

        # let
        self._write_token(self.token_type, self.token)  # type: ignore

        # varName
        assert self.jack_tokenizer.has_more_tokens()
        self._advance()
        self._write_token(self.token_type, self.token)  # type: ignore

        # [expression]
        next_token = self.jack_tokenizer.look_ahead()
        if next_token == "[":
            # The symbol [
            assert self.jack_tokenizer.has_more_tokens()
            self._advance()
            self._write_token(self.token_type, self.token)  # type: ignore

            # expression
            assert self.jack_tokenizer.has_more_tokens()
            self._advance()
            self.compile_expression()

            # The symbol ]
            assert self.jack_tokenizer.has_more_tokens()
            self._advance()
            self._write_token(self.token_type, self.token)  # type: ignore

        # The symbol =
        assert self.jack_tokenizer.has_more_tokens()
        self._advance()
        self._write_token(self.token_type, self.token)  # type: ignore

        # expression
        assert self.jack_tokenizer.has_more_tokens()
        self._advance()
        self.compile_expression()

        # The ; symbol
        assert self.jack_tokenizer.has_more_tokens()
        self._advance()
        self._write_token(self.token_type, self.token)  # type: ignore

        self._close_grammar("letStatement")

    def _write_expression_body(self) -> None:
        """Write '('expression')''{statements}'."""
        # The ( symbol
        self._write_token(self.token_type, self.token)  # type: ignore

        # expression
        assert self.jack_tokenizer.has_more_tokens()
        self._advance()
        self.compile_expression()

        # The ) symbol
        assert self.jack_tokenizer.has_more_tokens()
        self._advance()
        self._write_token(self.token_type, self.token)  # type: ignore

        # '{statements}'
        assert self.jack_tokenizer.has_more_tokens()
        self._advance()
        self._write_body()

    def _write_body(self) -> None:
        """Write '{statements}'."""
        # The { symbol
        self._write_token(self.token_type, self.token)  # type: ignore

        # statements
        next_token = self.jack_tokenizer.look_ahead()
        if next_token != "}":
            assert self.jack_tokenizer.has_more_tokens()
            self._advance()
            self.compile_statements()
        else:
            self._open_grammar("statements")
            self._close_grammar("statements")

        # The } symbol
        assert self.jack_tokenizer.has_more_tokens()
        self._advance()
        self._write_token(self.token_type, self.token)  # type: ignore

    def compile_if(self) -> None:
        """Compile an `if` statement, possibly with a trailing else clause."""
        self._open_grammar("ifStatement")

        # if
        self._write_token(self.token_type, self.token)  # type: ignore

        # '('expression')''{statements}'
        assert self.jack_tokenizer.has_more_tokens()
        self._advance()
        self._write_expression_body()

        next_token = self.jack_tokenizer.look_ahead()
        if next_token == "else":
            assert self.jack_tokenizer.has_more_tokens()
            self._advance()
            self._write_token(self.token_type, self.token)  # type: ignore

            # '{statements}'
            assert self.jack_tokenizer.has_more_tokens()
            self._advance()
            self._write_body()

        self._close_grammar("ifStatement")

    def compile_while(self) -> None:
        """Compile a `while` statement."""
        self._open_grammar("whileStatement")

        # while
        self._write_token(self.token_type, self.token)  # type: ignore

        # '('expression')''{statements}'
        assert self.jack_tokenizer.has_more_tokens()
        self._advance()
        self._write_expression_body()

        self._close_grammar("whileStatement")

    def _write_subroutine_call(self):
        """Write the subroutine call."""
        # subroutineName | varName | className
        self._write_token(self.token_type, self.token)  # type: ignore

        next_token = self.jack_tokenizer.look_ahead()
        if next_token == ".":
            # The symbol .
            assert self.jack_tokenizer.has_more_tokens()
            self._advance()
            self._write_token(self.token_type, self.token)  # type: ignore

            # subroutineName
            assert self.jack_tokenizer.has_more_tokens()
            self._advance()
            self._write_token(self.token_type, self.token)  # type: ignore

        # The ( symbol
        assert self.jack_tokenizer.has_more_tokens()
        self._advance()
        self._write_token(self.token_type, self.token)  # type: ignore

        # The expression list
        assert self.jack_tokenizer.has_more_tokens()
        self._advance()
        self.compile_expression_list()

        # The ) symbol
        # We are guaranteed
        self._write_token(self.token_type, self.token)  # type: ignore

    def compile_do(self) -> None:
        """Compile a `do` statement."""
        self._open_grammar("doStatement")

        # do
        self._write_token(self.token_type, self.token)  # type: ignore

        assert self.jack_tokenizer.has_more_tokens()
        self._advance()
        self._write_subroutine_call()

        # The ; symbol
        assert self.jack_tokenizer.has_more_tokens()
        self._advance()
        self._write_token(self.token_type, self.token)  # type: ignore

        self._close_grammar("doStatement")

    def compile_return(self) -> None:
        """Compile a `return` statement."""
        self._open_grammar("returnStatement")

        # return
        self._write_token(self.token_type, self.token)  # type: ignore

        next_token = self.jack_tokenizer.look_ahead()
        if next_token != ";":
            assert self.jack_tokenizer.has_more_tokens()
            self._advance()
            self.compile_expression()

        # The ; symbol
        assert self.jack_tokenizer.has_more_tokens()
        self._advance()
        self._write_token(self.token_type, self.token)  # type: ignore

        self._close_grammar("returnStatement")

    def compile_expression(self) -> None:
        """Compile an `expression` statement."""
        self._open_grammar("expression")

        # term
        self.compile_term()

        next_token = self.jack_tokenizer.look_ahead()

        # (op term)*
        while next_token in get_args(Op):
            # op
            assert self.jack_tokenizer.has_more_tokens()
            self._advance()
            self._write_token(self.token_type, self.token)  # type: ignore

            # term
            assert self.jack_tokenizer.has_more_tokens()
            self._advance()
            self.compile_term()

            next_token = self.jack_tokenizer.look_ahead()

        self._close_grammar("expression")

    def compile_term(self) -> None:
        """Compile a term.

        If the current token is an `IDENTIFIER`, the routine distinguishes
        between a variable, an array entry, or a subroutine call.
        A single look-ahead token, which may be one of `[`, `(`, or `.` is used
        to distinguish between the possibilities.
        Any other token is not part of this term will not be advanced over.
        """
        self._open_grammar("term")

        if self.token_type == "stringConstant":
            # stringConstant
            self._write_token(self.token_type, self.token.replace('"', ""))  # type: ignore
        elif self.token_type in ("integerConstant", "keyword"):
            # integerConstant | keywordConstant
            self._write_token(self.token_type, self.token)  # type: ignore
        elif self.token_type == "identifier":
            # varName | varName'['expression']' | subroutineCall
            next_token = self.jack_tokenizer.look_ahead()

            if next_token == "[":
                # varName'['expression']'

                # varName
                self._write_token(self.token_type, self.token)  # type: ignore

                # The [ symbol
                assert self.jack_tokenizer.has_more_tokens()
                self._advance()
                self._write_token(self.token_type, self.token)  # type: ignore

                # expression
                assert self.jack_tokenizer.has_more_tokens()
                self._advance()
                self.compile_expression()

                # The ] symbol
                assert self.jack_tokenizer.has_more_tokens()
                self._advance()
                self._write_token(self.token_type, self.token)  # type: ignore
            elif next_token in ("(", "."):
                self._write_subroutine_call()
            else:
                # varName
                self._write_token(self.token_type, self.token)  # type: ignore
        elif self.token == "(":
            # '('expression')'

            # '('
            self._write_token(self.token_type, self.token)  # type: ignore

            # expression
            assert self.jack_tokenizer.has_more_tokens()
            self._advance()
            self.compile_expression()

            # ')'
            assert self.jack_tokenizer.has_more_tokens()
            self._advance()
            self._write_token(self.token_type, self.token)  # type: ignore
        elif self.token_type == "symbol":
            # unaryOp term

            # 'unaryOp'
            self._write_token(self.token_type, self.token)  # type: ignore

            # term
            assert self.jack_tokenizer.has_more_tokens()
            self._advance()
            self.compile_term()
        else:
            raise RuntimeError(
                f"Token type {self.token_type} with token {self.token} not recognized as a term"
            )

        self._close_grammar("term")

    def compile_expression_list(self) -> None:
        """Compile a (possibly empty) comma-separated list of expressions."""
        self._open_grammar("expressionList")

        if self.token != ")":
            # expression
            self.compile_expression()

            next_token = self.jack_tokenizer.look_ahead()
            if next_token == ")":
                # Advance at the end of the list, so that self.token is
                # the same irrespective of whether the expression list
                # was empty or not
                assert self.jack_tokenizer.has_more_tokens()
                self._advance()

            # (',' expression)*
            while next_token != ")":
                # The , symbol
                assert self.jack_tokenizer.has_more_tokens()
                self._advance()
                self._write_token(self.token_type, self.token)  # type: ignore

                # expression
                assert self.jack_tokenizer.has_more_tokens()
                self._advance()
                self.compile_expression()
                next_token = self.jack_tokenizer.look_ahead()

                if next_token == ")":
                    # Advance at the end of the list, so that self.token is
                    # the same irrespective of whether the expression list
                    # was empty or not
                    assert self.jack_tokenizer.has_more_tokens()
                    self._advance()

        self._close_grammar("expressionList")
