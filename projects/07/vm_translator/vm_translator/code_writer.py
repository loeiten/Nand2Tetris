"""Module containing the CodeWriter class."""


from pathlib import Path
from typing import Literal


class CodeWriter:
    """Class which writes symbolic Hack assembly code."""

    def __init__(self, path: str) -> None:
        """Open the output file/stream and gets ready to write into it.

        Args:
            path (str): Path to file to write to.
        """
        self.file = Path(path).resolve().open("r")

    def write_arithmetic(self, command: str) -> None:
        """Write to the output file the assembly code that implements the given arithmetic command.

        Args:
            command (str): The command to translate into assembly
        """
        # Memory mapping:
        # SP - 0 - points to the next free stack address
        # LCL - 1
        # ARG - 2
        # THIS - 3
        # THAT - 4
        # temp - 5-17
        # static - 16-255
        # stack - 256-2047
        # pointer - 3-4 - pointer 0 => RAM[3], pointer 1 => RAM[4]
        # general purpose registers - 13-15
        # constant i => RAM[i]
        # segment i => RAM[*segment_pointer + i]

        # Write the command
        self.file.write(f"// {command}\n")

        # Decrement the stack pointer for binary operations
        unary_operators = (
            "neg",
            "not",
        )
        if command not in unary_operators:
            # Decrement the current value of stack pointer
            # We do this by first dereferencing the memory location...
            self.file.write(
                f"//{' '*4}Dereferencing stack pointer\n"
                "@SP  // Set A to 0 (side effect: M is set to RAM[0])\n"
                "A=M  // Set A to M (side effect: M is set to RAM[M])\n"
                "D=A  // Set D to RAM[M]\n"
                f"//{' '*4}Decrementing the stack pointer\n"
                "D=D-1\n"
                "@SP  // Set A to 0 (side effect: M is set to RAM[0]\n"
                "M=D  // Store D to RAM[0]\n"
            )

    def write_push_pop(
        self,
        command: Literal["C_PUSH", "C_POP"],
        segment: Literal[
            "local", "argument", "this", "that", "constant", "static", "pointer", "temp"
        ],
        index: int,
    ) -> None:
        """Write to the output file the assembly code that implements the given command.

        The command can be either C_PUSH or C_POP

        Args:
            command (Literal["C_PUSH", "C_POP"]): The command to translate into assembly
            segment (Literal["local", "argument", "this", "that", "constant", "static", "pointer",
            "temp"]):
                Which virtual memory segment to push from/pop to
            index (int): Segment index to push from/pop to
        """

    def close(self) -> None:
        """Close the output file."""
        self.file.close()
