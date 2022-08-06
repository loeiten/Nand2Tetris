"""Module containing the VMWriter class."""

from typing import Literal, Union

NonConstVirtualSegments = Literal[
    "ARG", "LOCAL", "STATIC", "THIS", "THAT", "POINTER", "TEMP"
]
ConstVirtualSegments = Literal["CONST"]
VirtualSegments = Union[NonConstVirtualSegments, ConstVirtualSegments]

Arithmetic = Literal["ADD", "SUB", "NEG", "EQ", "GT", "LT", "AND", "OR", "NOT"]


class VMWriter:
    """Class which writes VM code."""

    def __init__(self) -> None:
        """Create a new output .vm file and prepares it for writing."""

    def write_push(self, segment: VirtualSegments, index: int) -> None:
        """Write a VM push command.

        Args:
            segment (VIRTUAL_SEGMENTS): The segment to write
            index (int): The index to write
        """

    def write_pop(self, segment: NonConstVirtualSegments, index: int) -> None:
        """Write a VM pop command.

        Args:
            segment (NON_CONST_VIRTUAL_SEGMENTS): The segment to write
            index (int): The index to write
        """

    def write_arithmetic(self, command: Arithmetic) -> None:
        """Write a VM arithmetic-logical command.

        Args:
            command (ARITHMETIC): The command to write
        """

    def write_label(self, label: str) -> None:
        """Write a VM label command.

        Args:
            label (str): The label to write
        """

    def write_goto(self, label: str) -> None:
        """Write a VM goto command.

        Args:
            label (str): The label to go to
        """

    def write_if(self, label: str) -> None:
        """Write a VM if-goto command.

        Args:
            label (str): The label to go to
        """

    def write_call(self, name: str, n_args: int) -> None:
        """Write a VM call command.

        Args:
            name (str): The function name to call
            n_args (int): The number of arguments
        """

    def write_function(self, name: str, n_locals: int) -> None:
        """Write a VM function command.

        Args:
            name (str): The name of the function to write
            n_locals (int): The number of local variables
        """

    def write_return(self) -> None:
        """Write a VM return command."""

    def close(self) -> None:
        """Close the output file."""
