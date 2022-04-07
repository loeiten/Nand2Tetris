"""Module containing the CodeWriter class."""


from typing import Literal


class CodeWriter:
    """Class which writes symbolic Hack assembly code."""

    def __init__(self, path: str) -> None:
        """Open the output file/stream and gets ready to write into it.

        Args:
            path (str): Path to file to write to.
        """

    def write_arithmetic(self, command: str) -> None:
        """Write to the output file the assembly code that implements the given arithmetic command.

        Args:
            command (str): The command to translate into assembly
        """

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
