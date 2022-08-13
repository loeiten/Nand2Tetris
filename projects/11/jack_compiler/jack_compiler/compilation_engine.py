"""Module containing the CompilationEngine class."""

from io import TextIOWrapper
from pathlib import Path
from typing import Dict, Literal, Optional, Tuple, Union, cast, get_args

from jack_compiler import KIND
from jack_compiler.jack_tokenizer import JackTokenizer
from jack_compiler.symbol_table import SymbolTable
from jack_compiler.vm_writer import VMWriter

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
OpName = Literal["ADD", "SUB", "MUL", "DIV", "AND", "OR", "LT", "GT", "EQ"]


class CompilationEngine:
    """
    Class which generates the compiler's output.

    Note:
        There is no operator precedence of expressions.
        Expressions are simply compiled from left to the right.
    """

    token_map = {
        "KEYWORD": {"text": "keyword", "function_name": "keyword"},
        "SYMBOL": {"text": "symbol", "function_name": "symbol"},
        "IDENTIFIER": {"text": "identifier", "function_name": "identifier"},
        "INT_CONST": {"text": "integerConstant", "function_name": "int_val"},
        "STRING_CONST": {"text": "stringConstant", "function_name": "string_val"},
    }
    segment_map = {"STATIC": "STATIC", "FIELD": "THIS", "ARG": "ARG", "VAR": "LOCAL"}
    op_map = {
        "+": "ADD",
        "-": "SUB",
        "*": "MUL",
        "/": "DIV",
        "&": "AND",
        "|": "OR",
        "<": "LT",
        ">": "GT",
        "=": "EQ",
    }

    def __init__(self, jack_tokenizer: JackTokenizer, out_file: TextIOWrapper) -> None:
        """Create a new compilation engine with the given input and output.

        Args:
            jack_tokenizer (JackTokenizer): The tokenizer
            out_file (TextIOWrapper): Stream to the output file

        Raises:
            RuntimeError: If the file does not contain any tokens
        """
        self._jack_tokenizer = jack_tokenizer
        self._out_file = out_file
        self._indentation = 0

        self._symbol_tables = {"class": SymbolTable(), "subroutine": SymbolTable()}
        self._context_details = {
            "class_name": "",
            "subroutine_type": "",
            "return_type": "",
            "assign_to": "",
            "array_lhs": False,
            "if_statement": False,
            "while_statement": False,
            "expression_list_count": list(),
        }
        # We start on -2 as the first thing the if and while compiler is going to do is
        # to increment these values by 2
        self._labels = {
            "while_counter": -2,
            "if_counter": -2,
            "while": list(),
            "if": list(),
        }

        self.token = {"type": "", "token": ""}

        self._vm_writer = VMWriter(Path(out_file.name).with_suffix(".vm").open("w"))

        if not jack_tokenizer.has_more_tokens():
            raise RuntimeError(
                f"Running tokenizer on empty file {jack_tokenizer.file.name}"
            )
        # Above we use the file to check whether we have more tokens
        # This alters the file pointer of the file
        # Hence we must reset the pointer:
        self._jack_tokenizer.reset()

    def _advance(self) -> None:
        """Advance the tokenizer."""
        self._jack_tokenizer.advance()

        token_type = self._jack_tokenizer.token_type()
        func = getattr(
            self._jack_tokenizer, self.token_map[token_type]["function_name"]
        )
        self.token["token"] = func()
        self.token["type"] = self.token_map[token_type]["text"]
        if token_type == "KEYWORD":
            self.token["token"] = self.token["token"].lower()

    def compile_tokens_only(self) -> None:
        """Only compile tokens."""
        while self._jack_tokenizer.has_more_tokens():
            self._advance()
            # Type ignore as mypy doesn't detect that we are ensuring the
            # correct input type for token_type
            self._write_token(
                token_type=self.token["type"], token=self.token["token"]  # type: ignore
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
            kind = self._symbol_tables["subroutine"].kind_of(token_str)
            table = self._symbol_tables["subroutine"]
            if kind is None:
                # Search then in the class table
                kind = self._symbol_tables["class"].kind_of(token_str)
                table = self._symbol_tables["class"]
            if kind is None:
                # We must be dealing with either a class or a subroutine
                # If it is a subroutine name it must be followed by a "("
                class_or_subroutine = (
                    "subroutine"
                    if self._jack_tokenizer.look_ahead() == "("
                    else "class"
                )
                cur_token_type = (
                    f"{class_or_subroutine}_{'definition' if definition else 'usage'}"
                )
            else:
                index = table.index_of(token_str)
                cur_token_type = (
                    f"{kind.lower()}_{index}_{'definition' if definition else 'usage'}"
                )
        else:
            cur_token_type = token_type
        token = (
            token_str.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
        )
        self._out_file.write(
            f"{' '*self._indentation}<{cur_token_type}> {token} </{cur_token_type}>\n"
        )

    def _open_grammar(self, grammar_type: NonTerminalElement) -> None:
        """Open a grammar body.

        Args:
            grammar_type (NON_TERMINAL_ELEMENT): The grammar tag
        """
        self._out_file.write(f"{' '*self._indentation}<{grammar_type}>\n")
        # Increase the current indentation
        self._indentation += 2

    def _close_grammar(self, grammar_type: NonTerminalElement) -> None:
        """Close the grammar body.

        Args:
            grammar_type (NON_TERMINAL_ELEMENT): The grammar tag
        """
        # Decrease the current indentation
        self._indentation = max(0, self._indentation - 2)
        self._out_file.write(f"{' '*self._indentation}</{grammar_type}>\n")

    def compile_class(self) -> None:
        """Compile a complete class."""
        assert self._jack_tokenizer.has_more_tokens()
        self._advance()
        if self.token["token"] != "class":
            raise RuntimeError(
                f"{self._jack_tokenizer.file.name} did not start with a definition of 'class'"
            )
        # Write class
        self._open_grammar("class")
        # Type ignore as mypy doesn't detect that we are ensuring the
        # correct input type for token_type
        self._write_token(self.token["type"], self.token["token"])  # type: ignore

        # Class name
        assert self._jack_tokenizer.has_more_tokens()
        self._advance()
        # This is a definition
        self._write_token(self.token["type"], self.token["token"], definition=True)  # type: ignore
        # Set the class name
        self._context_details["class_name"] = self.token["token"]

        # The { symbol
        assert self._jack_tokenizer.has_more_tokens()
        self._advance()
        self._write_token(self.token["type"], self.token["token"])  # type: ignore

        # Zero or more classVarDec
        next_token = self._jack_tokenizer.look_ahead()
        while next_token in ("static", "field"):
            assert self._jack_tokenizer.has_more_tokens()
            self._advance()
            self.compile_class_var_dec()
            next_token = self._jack_tokenizer.look_ahead()

        # Zero or more subroutineDec
        next_token = self._jack_tokenizer.look_ahead()
        while next_token in ("constructor", "function", "method"):
            assert self._jack_tokenizer.has_more_tokens()
            self._advance()
            self.compile_subroutine_dec()
            next_token = self._jack_tokenizer.look_ahead()

        # The } symbol
        assert self._jack_tokenizer.has_more_tokens()
        self._advance()
        self._write_token(self.token["type"], self.token["token"])  # type: ignore

        self._close_grammar("class")

    def compile_class_var_dec(self) -> None:
        """Compile a static variable declaration or a field variable declaration."""
        self._open_grammar("classVarDec")

        # static | field
        self._write_token(self.token["type"], self.token["token"])  # type: ignore
        kind = self.token["token"].upper()
        if kind not in get_args(KIND):
            raise RuntimeError(f"Unknown kind: {kind}, must be one of {KIND}")

        # type
        assert self._jack_tokenizer.has_more_tokens()
        self._advance()
        # We may be dealing with a class, which in this case is being used
        self._write_token(self.token["type"], self.token["token"], definition=False)  # type: ignore
        identifier_type = self.token["token"]

        # varName
        assert self._jack_tokenizer.has_more_tokens()
        self._advance()
        # Here the variables are being defined
        # Add to the class table before writing
        # mypy seem unable to detect that we are checking for the correct type
        self._symbol_tables["class"].define(
            name=self.token["token"], identifier_type=identifier_type, kind=kind  # type: ignore
        )
        self._write_token(self.token["type"], self.token["token"], definition=True)  # type: ignore

        assert self._jack_tokenizer.has_more_tokens()
        self._advance()

        # (, varName)*
        while self.token["token"] == ",":
            # The , symbol
            self._write_token(self.token["type"], self.token["token"])  # type: ignore

            # varName
            assert self._jack_tokenizer.has_more_tokens()
            self._advance()
            # Here the variables are being defined
            # Add to the class table before writing
            # mypy seem unable to detect that we are checking for the correct type
            self._symbol_tables["class"].define(
                name=self.token["token"], identifier_type=identifier_type, kind=kind  # type: ignore
            )
            self._write_token(
                self.token["type"], self.token["token"], definition=True  # type: ignore
            )

            assert self._jack_tokenizer.has_more_tokens()
            self._advance()

        # The ; symbol
        self._write_token(self.token["type"], self.token["token"])  # type: ignore

        self._close_grammar("classVarDec")

    def compile_subroutine_dec(self) -> None:
        """Compile a complete method, function or constructor."""
        self._open_grammar("subroutineDec")

        # constructor | function | method
        self._write_token(self.token["type"], self.token["token"])  # type: ignore
        self._context_details["subroutine_type"] = self.token["token"]
        if self._context_details["subroutine_type"] == "method":
            # Populate the symbol table with the implicit `this`
            self._symbol_tables["subroutine"].define(
                name="this",
                identifier_type=self._context_details["class_name"],
                kind="ARG",
            )

        # void | type
        assert self._jack_tokenizer.has_more_tokens()
        self._advance()
        self._write_token(self.token["type"], self.token["token"])  # type: ignore
        self._context_details["return_type"] = self.token["token"]

        # subroutineName
        assert self._jack_tokenizer.has_more_tokens()
        self._advance()
        # We are here defining the subroutine
        self._write_token(self.token["type"], self.token["token"], definition=True)  # type: ignore
        subroutine_name = self.token["token"]

        # The ( symbol
        assert self._jack_tokenizer.has_more_tokens()
        self._advance()
        self._write_token(self.token["type"], self.token["token"])  # type: ignore

        # parameterList
        next_token = self._jack_tokenizer.look_ahead()
        if next_token != ")":
            assert self._jack_tokenizer.has_more_tokens()
            self._advance()
            self.compile_parameter_list()
        else:
            self._open_grammar("parameterList")
            self._close_grammar("parameterList")

        # The ) symbol
        assert self._jack_tokenizer.has_more_tokens()
        self._advance()
        self._write_token(self.token["type"], self.token["token"])  # type: ignore

        # As the subroutine table has been populated, we can now write vm statements
        self._vm_writer.write_function(
            name=f"{self._context_details['class_name']}.{subroutine_name}",
            n_locals=self._symbol_tables["subroutine"].var_count("VAR"),
        )

        # subRoutine body
        assert self._jack_tokenizer.has_more_tokens()
        self._advance()
        self.compile_subroutine_body()

        self._close_grammar("subroutineDec")

        # Reset the tables["subroutine"]
        self._symbol_tables["subroutine"] = SymbolTable()

    def compile_parameter_list(self) -> None:
        """Compile a (possibly empty) parameter list.

        Does not handle the enclosing "()"
        """
        self._open_grammar("parameterList")
        kind: KIND = "ARG"
        cast(KIND, kind)

        next_token = self._jack_tokenizer.look_ahead()
        if next_token != ")":
            # Add the implicit `this` parameter if present in the subroutine table
            if self._symbol_tables["subroutine"].kind_of("this") is not None:
                self._write_token("identifier", "myClass", definition=False)
                self._write_token("identifier", "this", definition=True)
                self._write_token("symbol", ",")

            # type
            self._write_token(self.token["type"], self.token["token"])  # type: ignore
            identifier_type = self.token["token"]

            # varName
            assert self._jack_tokenizer.has_more_tokens()
            self._advance()
            # Add to the subroutine table before writing
            self._symbol_tables["subroutine"].define(
                name=self.token["token"], identifier_type=identifier_type, kind=kind
            )
            # Here the variables are being defined
            self._write_token(
                self.token["type"], self.token["token"], definition=True  # type: ignore
            )

            next_token = self._jack_tokenizer.look_ahead()
            while next_token == ",":
                # ,
                assert self._jack_tokenizer.has_more_tokens()
                self._advance()
                self._write_token(self.token["type"], self.token["token"])  # type: ignore

                # type
                assert self._jack_tokenizer.has_more_tokens()
                self._advance()
                self._write_token(self.token["type"], self.token["token"])  # type: ignore
                identifier_type = self.token["token"]

                # varName
                assert self._jack_tokenizer.has_more_tokens()
                self._advance()
                # Here the variables are being defined
                # Add to the subroutine table before writing
                self._symbol_tables["subroutine"].define(
                    name=self.token["token"], identifier_type=identifier_type, kind=kind
                )
                self._write_token(
                    self.token["type"],  # type: ignore
                    self.token["token"],
                    definition=True,
                )

                next_token = self._jack_tokenizer.look_ahead()

        self._close_grammar("parameterList")

    def compile_subroutine_body(self) -> None:
        """Compile a subroutine's body."""
        self._open_grammar("subroutineBody")

        # The { symbol
        self._write_token(self.token["type"], self.token["token"])  # type: ignore

        # varDec
        next_token = self._jack_tokenizer.look_ahead()
        while next_token == "var":
            assert self._jack_tokenizer.has_more_tokens()
            self._advance()
            self.compile_var_dec()
            next_token = self._jack_tokenizer.look_ahead()

        # If we are dealing with the constructor
        if self._context_details["subroutine_type"] == "constructor":
            # Pushes size of object
            self._vm_writer.write_push(
                "CONST", self._symbol_tables["class"].var_count("FIELD")
            )
            # Allocates object
            self._vm_writer.write_call("Memory.alloc", 1)
            # Anchors this at the base address
            self._vm_writer.write_pop("POINTER", 0)

        # statements
        next_token = self._jack_tokenizer.look_ahead()
        if next_token != "}":
            assert self._jack_tokenizer.has_more_tokens()
            self._advance()
            self.compile_statements()

        # The } symbol
        assert self._jack_tokenizer.has_more_tokens()
        self._advance()
        self._write_token(self.token["type"], self.token["token"])  # type: ignore

        self._close_grammar("subroutineBody")

    def compile_var_dec(self) -> None:
        """Compile a var declaration."""
        self._open_grammar("varDec")
        kind: KIND = "VAR"

        # var
        self._write_token(self.token["type"], self.token["token"])  # type: ignore

        # type
        assert self._jack_tokenizer.has_more_tokens()
        self._advance()
        self._write_token(self.token["type"], self.token["token"])  # type: ignore
        identifier_type = self.token["token"]

        # varName
        assert self._jack_tokenizer.has_more_tokens()
        self._advance()
        # Here the tokens are being defined
        # Add to the subroutine table before writing
        self._symbol_tables["subroutine"].define(
            name=self.token["token"], identifier_type=identifier_type, kind=kind
        )
        self._write_token(self.token["type"], self.token["token"], definition=True)  # type: ignore

        # (, varName)*
        next_token = self._jack_tokenizer.look_ahead()
        while next_token == ",":
            # The , symbol
            assert self._jack_tokenizer.has_more_tokens()
            self._advance()
            self._write_token(self.token["type"], self.token["token"])  # type: ignore

            # varName
            assert self._jack_tokenizer.has_more_tokens()
            self._advance()
            # Here the tokens are being defined
            # Add to the subroutine table before writing
            self._symbol_tables["subroutine"].define(
                name=self.token["token"], identifier_type=identifier_type, kind=kind
            )
            self._write_token(
                self.token["type"],  # type: ignore
                self.token["token"],
                definition=True,
            )

            next_token = self._jack_tokenizer.look_ahead()

        # The symbol ;
        assert self._jack_tokenizer.has_more_tokens()
        self._advance()
        self._write_token(self.token["type"], self.token["token"])  # type: ignore

        self._close_grammar("varDec")

    def compile_statements(self) -> None:
        """Compile a sequence of statements.

        Does not handle the enclosing "{}"
        """
        self._open_grammar("statements")

        while self.token["token"] in ("let", "if", "while", "do", "return"):
            if self.token["token"] == "let":
                self.compile_let()
            elif self.token["token"] == "if":
                self.compile_if()
            elif self.token["token"] == "while":
                self.compile_while()
            elif self.token["token"] == "do":
                self.compile_do()
            elif self.token["token"] == "return":
                self.compile_return()
            next_token = self._jack_tokenizer.look_ahead()
            if next_token in ("let", "if", "while", "do", "return"):
                assert self._jack_tokenizer.has_more_tokens()
                self._advance()

        self._close_grammar("statements")

    def compile_let(self) -> None:
        """Compile a `let` statement."""
        self._open_grammar("letStatement")

        # let
        self._write_token(self.token["type"], self.token["token"])  # type: ignore

        # varName
        assert self._jack_tokenizer.has_more_tokens()
        self._advance()
        self._write_token(self.token["type"], self.token["token"])  # type: ignore
        # Get the address we want to pop to
        self._context_details["assign_to"] = self.token["token"]

        # [expression]
        next_token = self._jack_tokenizer.look_ahead()
        if next_token == "[":
            # The symbol [
            assert self._jack_tokenizer.has_more_tokens()
            self._advance()
            self._write_token(self.token["type"], self.token["token"])  # type: ignore

            # expression
            assert self._jack_tokenizer.has_more_tokens()
            self._advance()
            self.compile_expression()

            # The symbol ]
            assert self._jack_tokenizer.has_more_tokens()
            self._advance()
            self._write_token(self.token["type"], self.token["token"])  # type: ignore

            self._context_details["array_lhs"] = True

        # The symbol =
        assert self._jack_tokenizer.has_more_tokens()
        self._advance()
        self._write_token(self.token["type"], self.token["token"])  # type: ignore

        # expression
        assert self._jack_tokenizer.has_more_tokens()
        self._advance()
        self.compile_expression()

        # The ; symbol
        assert self._jack_tokenizer.has_more_tokens()
        self._advance()
        self._write_token(self.token["type"], self.token["token"])  # type: ignore

        if self._context_details["array_lhs"]:
            # In order not to overwrite the array pointer we must use the 
            # general solution for array access
            # NOTE: We can use this even if the RHS is not an array
            # Dereference the RHS array
            self._vm_writer.write_pop(segment="POINTER", index=1)
            self._vm_writer.write_push(segment="THAT", index=0)
            # Push the value to temp
            self._vm_writer.write_pop(segment="TEMP", index=0)
            # Pop the LHS address to the array pointer
            self._vm_writer.write_pop(segment="POINTER", index=1)
            # Push the RHS value to the stack
            self._vm_writer.write_push(segment="TEMP", index=0)
            # Add the value to the LHS address
            self._vm_writer.write_pop(segment="THAT", index=0)
        else:
            # We are dealing with a normal variable
            # Write the pop (assign) command
            table, segment = self._get_table_segment(self._context_details["assign_to"])
            # mypy doesn't recognize the segment_map
            self._vm_writer.write_pop(
                segment=self.segment_map[segment],  # type: ignore
                index=table.index_of(self._context_details["assign_to"]),
            )

        self._context_details["array_lhs"] = False
        self._close_grammar("letStatement")

    def _write_expression_body(self) -> None:
        """Write '('expression')''{statements}'."""
        # The ( symbol
        self._write_token(self.token["type"], self.token["token"])  # type: ignore

        # expression
        assert self._jack_tokenizer.has_more_tokens()
        self._advance()
        self.compile_expression()

        # The ) symbol
        assert self._jack_tokenizer.has_more_tokens()
        self._advance()
        self._write_token(self.token["type"], self.token["token"])  # type: ignore

        if self._context_details["while_statement"]:
            # Negate the expression in order to simplify the vm code
            self._vm_writer.write_arithmetic(command="NOT")
            # NOTE: We use the list instead of the counter
            self._vm_writer.write_if(label=f"WHILE_END_L{self._labels['while'][-1]+1}")
        elif self._context_details["if_statement"]:
            # Negate the expression in order to simplify the vm code
            self._vm_writer.write_arithmetic(command="NOT")
            # NOTE: We use the list instead of the counter
            self._vm_writer.write_if(label=f"NOT_IF_L{self._labels['if'][-1]}")

        # '{statements}'
        assert self._jack_tokenizer.has_more_tokens()
        self._advance()
        self._write_body()

    def _write_body(self) -> None:
        """Write '{statements}'."""
        # The { symbol
        self._write_token(self.token["type"], self.token["token"])  # type: ignore

        # statements
        next_token = self._jack_tokenizer.look_ahead()
        if next_token != "}":
            assert self._jack_tokenizer.has_more_tokens()
            self._advance()
            self.compile_statements()
        else:
            self._open_grammar("statements")
            self._close_grammar("statements")

        # The } symbol
        assert self._jack_tokenizer.has_more_tokens()
        self._advance()
        self._write_token(self.token["type"], self.token["token"])  # type: ignore

    def compile_if(self) -> None:
        """Compile an `if` statement, possibly with a trailing else clause."""
        self._open_grammar("ifStatement")

        # As we can have nested statements we need to have a structure to account for this
        # We will to this by appending and popping a list
        # We start by add 2 to the counter
        # (one for an if statement, one for a potential else statement)
        self._labels["if_counter"] += 2
        self._labels["if"].append(self._labels["if_counter"])

        # if
        self._write_token(self.token["type"], self.token["token"])  # type: ignore

        # '('expression')''{statements}'
        assert self._jack_tokenizer.has_more_tokens()
        self._advance()
        self._write_expression_body()

        next_token = self._jack_tokenizer.look_ahead()
        if next_token == "else":
            # Add the goto L2 and label L1 before compiling the statements
            self._vm_writer.write_goto(label=f"IF_END_L{self._labels['if'][-1] + 1}")
            self._vm_writer.write_label(label=f"NOT_IF_L{self._labels['if'][-1]}")
            assert self._jack_tokenizer.has_more_tokens()
            self._advance()
            self._write_token(self.token["type"], self.token["token"])  # type: ignore

            # '{statements}'
            assert self._jack_tokenizer.has_more_tokens()
            self._advance()
            self._write_body()

            # Add the L2 label
            self._vm_writer.write_label(label=f"IF_END_L{self._labels['if'][-1] + 1}")
        else:
            self._vm_writer.write_label(label=f"NOT_IF_L{self._labels['if'][-1]}")

        # Pop the list
        self._labels["if"].pop()
        self._close_grammar("ifStatement")

    def compile_while(self) -> None:
        """Compile a `while` statement."""
        self._open_grammar("whileStatement")

        # As we can have nested statements we need to have a structure to account for this
        # We will to this by appending and popping a list
        # We start by add 2 to the counter
        # (one for the start, and one for the end)
        self._labels["while_counter"] += 2
        self._labels["while"].append(self._labels["while_counter"])

        # while
        self._write_token(self.token["type"], self.token["token"])  # type: ignore

        # Add label L1
        self._vm_writer.write_label(label=f"WHILE_START_L{self._labels['while'][-1]}")

        # '('expression')''{statements}'
        assert self._jack_tokenizer.has_more_tokens()
        self._advance()
        self._write_expression_body()

        # goto L1, label L2
        self._vm_writer.write_goto(label=f"WHILE_START_L{self._labels['while'][-1]}")
        self._vm_writer.write_label(label=f"WHILE_END_L{self._labels['while'][-1] + 1}")

        self._labels["while"].pop()
        self._close_grammar("whileStatement")

    def _write_subroutine_call(self):
        """Write the subroutine call."""
        # subroutineName | varName | className
        self._write_token(self.token["type"], self.token["token"])  # type: ignore
        token = self.token["token"]

        next_token = self._jack_tokenizer.look_ahead()
        if next_token == ".":
            # The symbol .
            assert self._jack_tokenizer.has_more_tokens()
            self._advance()
            self._write_token(self.token["type"], self.token["token"])  # type: ignore

            # subroutineName
            assert self._jack_tokenizer.has_more_tokens()
            self._advance()
            self._write_token(self.token["type"], self.token["token"])  # type: ignore
            subroutine_name = self.token["token"]
            call_name = f"{token}.{subroutine_name}"

            # We here check if the token is a variable name
            table, segment = self._get_table_segment(token)
            if segment is not None:
                # Since we have found the variable in one of the tables, 
                # we know that it must be a method we are calling
                is_method = True
                # We must push the object we are working on to the front of the argument list
                self._vm_writer.write_push(segment=segment, index=table.index_of(token))
        else:
            # If we have no "." accessor, we must be operating on this object
            call_name = f"{self._context_details['class_name']}.{token}"

            is_method = True
            # We are working on "this" object, and must push it in first in the argument list
            self._vm_writer.write_push(segment="POINTER", index=0)

        # The ( symbol
        assert self._jack_tokenizer.has_more_tokens()
        self._advance()
        self._write_token(self.token["type"], self.token["token"])  # type: ignore

        # The expression list
        assert self._jack_tokenizer.has_more_tokens()
        self._advance()
        self.compile_expression_list()

        # The ) symbol
        self._write_token(self.token["type"], self.token["token"])  # type: ignore

        # Write the call to the subroutine
        # We need to add +1 if we are calling a method
        expression_list_count = self._context_details["expression_list_count"].pop()
        if is_method:
            expression_list_count += 1

        self._vm_writer.write_call(name=call_name, n_args=expression_list_count)

    def compile_do(self) -> None:
        """Compile a `do` statement."""
        self._open_grammar("doStatement")

        # do
        self._write_token(self.token["type"], self.token["token"])  # type: ignore

        assert self._jack_tokenizer.has_more_tokens()
        self._advance()
        self._write_subroutine_call()

        # The ; symbol
        assert self._jack_tokenizer.has_more_tokens()
        self._advance()
        self._write_token(self.token["type"], self.token["token"])  # type: ignore

        self._close_grammar("doStatement")

    def compile_return(self) -> None:
        """Compile a `return` statement."""
        self._open_grammar("returnStatement")

        # return
        self._write_token(self.token["type"], self.token["token"])  # type: ignore

        next_token = self._jack_tokenizer.look_ahead()
        if next_token != ";":
            assert self._jack_tokenizer.has_more_tokens()
            self._advance()
            self.compile_expression()

        # The ; symbol
        assert self._jack_tokenizer.has_more_tokens()
        self._advance()
        self._write_token(self.token["type"], self.token["token"])  # type: ignore

        self._close_grammar("returnStatement")

    def compile_expression(self) -> None:
        """Compile an `expression` statement.

        Note:
            - There is no operator precedence of expressions.
              Expressions are simply compiled from left to the right.
            - A more industrial strength compiler would make a syntax tree
        """
        self._open_grammar("expression")

        # term
        self.compile_term()

        next_token = self._jack_tokenizer.look_ahead()

        # (op term)*
        while next_token in get_args(Op):
            cur_op = self.op_map[next_token]
            # op
            assert self._jack_tokenizer.has_more_tokens()
            self._advance()
            self._write_token(self.token["type"], self.token["token"])  # type: ignore

            # term
            assert self._jack_tokenizer.has_more_tokens()
            self._advance()
            self.compile_term()

            # As stack is postfixed, we will add the ops to the very end
            self._write_op(cur_op)

            next_token = self._jack_tokenizer.look_ahead()

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

        # Expressions in parantheses must be evaluated first
        if self.token["token"] == "(":
            # '('expression')'

            # '('
            self._write_token(self.token["type"], self.token["token"])  # type: ignore

            # expression
            assert self._jack_tokenizer.has_more_tokens()
            self._advance()
            self.compile_expression()

            # ')'
            assert self._jack_tokenizer.has_more_tokens()
            self._advance()
            self._write_token(self.token["type"], self.token["token"])  # type: ignore
        elif self.token["type"] == "stringConstant":
            # stringConstant
            string = self.token["token"].replace('"', "")

            # NOTE: The constructor is NOT String.new("string"), but String.new(6)
            # Use-cases:
            # foo("string")
            # let a = "string"
            # For both use cases we need to create a new string object and use appendChar to fill
            self._vm_writer.write_push(segment="CONST", index=len(string))
            for char in string:
                # NOTE: The character set follows the ASCII mapping, hence we can use ord
                self._vm_writer.write_push(segment="CONST", index=ord(char))
                # Two arguments: One for this and one for the character
                self._vm_writer.write_call(name="String.appendChar", n_args=2)

            self._write_token(self.token["type"], string)  # type: ignore
        elif self.token["type"] in ("integerConstant", "keyword"):
            # integerConstant | keywordConstant
            self._write_token(self.token["type"], self.token["token"])  # type: ignore
            if self.token["type"] == "integerConstant":
                self._vm_writer.write_push(segment="CONST", index=self.token["token"])
            elif self.token["token"] == "null":
                self._vm_writer.write_push(segment="CONST", index=0)
            elif self.token["token"] == "false":
                self._vm_writer.write_push(segment="CONST", index=0)
            elif self.token["token"] == "true":
                self._vm_writer.write_push(segment="CONST", index=1)
                self._vm_writer.write_arithmetic(command="NEG")
            elif self.token["token"] == "this":
                self._vm_writer.write_push(segment="POINTER", index=0)
        elif self.token["type"] == "identifier":
            # varName | varName'['expression']' | subroutineCall
            next_token = self._jack_tokenizer.look_ahead()

            if next_token == "[":
                # varName'['expression']'

                # varName
                self._write_token(self.token["type"], self.token["token"])  # type: ignore
                var_name = self.token["token"]
                table, segment = self._get_table_segment(var_name=var_name)
                self._vm_writer.write_push(
                    segment=self.segment_map[segment],  # type: ignore
                    index=table.index_of(var_name),
                )

                # The [ symbol
                assert self._jack_tokenizer.has_more_tokens()
                self._advance()
                self._write_token(self.token["type"], self.token["token"])  # type: ignore

                # expression
                assert self._jack_tokenizer.has_more_tokens()
                self._advance()
                self.compile_expression()

                # The ] symbol
                assert self._jack_tokenizer.has_more_tokens()
                self._advance()
                self._write_token(self.token["type"], self.token["token"])  # type: ignore

                # Add [expression] to varName
                self._vm_writer.write_arithmetic(command="ADD")

                # Assignments of arrays are dealt with in compile_let
                if not self._context_details["array_lhs"]:
                    # The topmost value in the stack is an address, we will now dereference it
                    # Set the address to the array segment pointer
                    self._vm_writer.write_pop(segment="POINTER", index=1)
                    # Obtain the value of the address pointed to by pointer 1
                    self._vm_writer.write_push(segment="THAT", index=0)
            elif next_token in ("(", "."):
                self._write_subroutine_call()
            else:
                # varName
                self._write_token(self.token["type"], self.token["token"])  # type: ignore
                var_name = self.token["token"]
                table, segment = self._get_table_segment(var_name=var_name)
                self._vm_writer.write_push(
                    segment=self.segment_map[segment],  # type: ignore
                    index=table.index_of(var_name),
                )
        elif self.token["type"] == "symbol":
            # unaryOp term

            # 'unaryOp'
            self._write_token(self.token["type"], self.token["token"])  # type: ignore
            cur_op = self.op_map[self.token["token"]]

            # term
            assert self._jack_tokenizer.has_more_tokens()
            self._advance()
            self.compile_term()

            # As stack is postfixed, we will add the ops to the very end
            self._write_op(cur_op)
        else:
            raise RuntimeError(
                f"Token type {self.token['type']} with token "
                f"{self.token['token']} not recognized as a term"
            )

        self._close_grammar("term")

    def _write_op(self, cur_op: OpName) -> None:
        """Write the op to vm code.

        Args:
            cur_op (OpName): The op to write
        """
        if cur_op == "MUL":
            self._vm_writer.write_call(name="Math.multiply", n_args=2)
        elif cur_op == "DIV":
            self._vm_writer.write_call(name="Math.divide", n_args=2)
        else:
            self._vm_writer.write_arithmetic(command=cur_op)

    def _get_table_segment(
        self, var_name: str
    ) -> Tuple[Dict[str, SymbolTable], Optional[KIND]]:
        """Return table and segment of the variable.

        Args:
            var_name (str): Name of the variable

        Returns:
            Tuple[Dict[str, SymbolTable], Optional[KIND]]: The var name, table and segment
        """
        table = self._symbol_tables["subroutine"]
        segment = table.kind_of(name=var_name)
        if segment is None:
            table = self._symbol_tables["class"]
            segment = table.kind_of(name=var_name)
        return table, segment

    def compile_expression_list(self) -> None:
        """Compile a (possibly empty) comma-separated list of expressions."""
        self._open_grammar("expressionList")
        # NOTE: We can have nested expression lists
        # Reset the expression list count
        self._context_details["expression_list_count"].append(0)

        if self.token["token"] != ")":
            # expression
            self.compile_expression()
            self._context_details["expression_list_count"][-1] += 1

            next_token = self._jack_tokenizer.look_ahead()
            if next_token == ")":
                # Advance at the end of the list, so that self.token["token"] is
                # the same irrespective of whether the expression list
                # was empty or not
                assert self._jack_tokenizer.has_more_tokens()
                self._advance()

            # (',' expression)*
            while next_token != ")":
                # The , symbol
                assert self._jack_tokenizer.has_more_tokens()
                self._advance()
                self._write_token(self.token["type"], self.token["token"])  # type: ignore

                # expression
                assert self._jack_tokenizer.has_more_tokens()
                self._advance()
                self.compile_expression()
                self._context_details["expression_list_count"][-1] += 1
                next_token = self._jack_tokenizer.look_ahead()

                if next_token == ")":
                    # Advance at the end of the list, so that self.token["token"] is
                    # the same irrespective of whether the expression list
                    # was empty or not
                    assert self._jack_tokenizer.has_more_tokens()
                    self._advance()

        self._close_grammar("expressionList")
