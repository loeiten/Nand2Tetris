"""Module containing Parser class."""

import re
from enum import Enum
from pathlib import Path
from typing import Literal


class CommandEnum(Enum):
    """
    Enum describing the possible commands.

    - has been replaced with _
    """

    ADD = "C_ARITHMETIC"
    SUB = "C_ARITHMETIC"
    NEG = "C_ARITHMETIC"
    EQ = "C_ARITHMETIC"
    GT = "C_ARITHMETIC"
    LT = "C_ARITHMETIC"
    AND = "C_ARITHMETIC"
    OR = "C_ARITHMETIC"
    NOT = "C_ARITHMETIC"
    PUSH = "C_PUSH"
    POP = "C_POP"
    LABEL = "C_LABEL"
    GOTO = "C_GOTO"
    IF_GOTO = "C_GOTO"
    FUNCTION = "C_FUNCTION"
    RETURN = "C_RETURN"
    CALL = "C_CALL"


class Parser:
    """Class parsing .vm files."""

    def __init__(self, path: str) -> None:
        """Open input file to parse.

        Args:
            path (str): Path to file to parse
        """
        self.file = Path(path).resolve().open("r")
        self.current_instruction = ""
        # Regexes
        starting_with_comment = r"^\s*(\/{2,}|\n)"
        self.ignore_re = re.compile(starting_with_comment)

    def __del__(self):
        """Close the file."""
        self.file.close()

    def has_more_commands(self) -> bool:
        """Return if the file has more commands.

        Returns:
            bool: True if the file has more lines
        """
        cur_pos = self.file.tell()
        # The return value of .readline() is unambiguous
        # It will return "" only on the last line
        # A blank line will be returned as "\n"
        next_line_not_empty = bool(self.file.readline())
        self.file.seek(cur_pos)
        return next_line_not_empty

    def advance(self) -> None:
        """Read the next instruction and make it the current instruction.

        Will populate self.current_instruction, and skip over whitespace and comments.
        If it reaches the end of the line self.current_instruction will be set to None.

        This method should be called only if has_more_lines is true.
        """
        found_line = False

        while not found_line:
            line = self.file.readline()
            # Check if we are at the end of the file
            if line == "":
                self.current_instruction = ""
                return

            # Check if this line can be skipped
            if self.ignore_re.match(line) is not None:
                continue

            # We've found an instruction
            found_line = True
            self.current_instruction = line

        # Remove any comments
        self.current_instruction = self.current_instruction.split("//")[0]
        # Remove trailing whitespaces
        self.current_instruction = self.current_instruction.rstrip().lstrip()

    def command_type(
        self,
    ) -> Literal[
        "C_ARITHMETIC",
        "C_PUSH",
        "C_POP",
        "C_LABEL",
        "C_GOTO",
        "C_IF",
        "C_FUNCTION",
        "C_RETURN",
        "C_CALL",
    ]:
        """Return the current command type.

        The current instructions are either
        - C_ARITHMETIC for add, sub, neg, eq, gt, lt, and, or, not
        - C_PUSH for push
        - C_POP for pop
        - C_LABEL for labels
        - C_GOTO for go to statements
        - C_IF for if statements
        - C_FUNCTION for functions
        - C_RETURN for returns
        - C_CALL for calls

        Returns:
            Literal["C_ARITHMETIC", "C_PUSH", "C_POP", "C_LABEL", "C_GOTO",
            "C_IF", "C_FUNCTION", "C_RETURN", "C_CALL"]:
                The command type
        """
        return CommandEnum[
            self.current_instruction.split()[0].replace("-", "_").upper()
        ].value

    def arg1(self) -> str:
        """Return the first argument of the current command.

        In case of C_ARITHMETIC the command itself (add, sub, etc.) is returned.
        Should not be called if the current command is C_RETURN.

        Returns:
            str: The first argument of the current command
        """
        command = self.current_instruction.split()[0]
        if CommandEnum[command] == "C_ARITHMETIC":
            return command
        return self.current_instruction.split()[1]

    def arg2(self) -> int:
        """Return the second argument of the current command.

        Should only be called if the current command is C_PUSH, C_POP, C_FUNCTION or C_CALL.

        Returns:
            int: The index of the virtual segment to use
        """
        return int(self.current_instruction.split()[2])
