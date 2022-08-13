"""Module containing the VMWriter class."""

from io import TextIOWrapper
from typing import Literal, Union

NonConstVirtualSegments = Literal[
    "ARG", "LOCAL", "STATIC", "THIS", "THAT", "POINTER", "TEMP"
]
ConstVirtualSegments = Literal["CONST"]
VirtualSegments = Union[NonConstVirtualSegments, ConstVirtualSegments]

Arithmetic = Literal["ADD", "SUB", "NEG", "EQ", "GT", "LT", "AND", "OR", "NOT"]


class VMWriter:
    """Class which writes VM code."""

    segment_map = {
        "ARG": "argument",
        "LOCAL": "local",
        "STATIC": "static",
        "FIELD": "this",
        "THIS": "this",
        "THAT": "that",
        "POINTER": "pointer",
        "TEMP": "temp",
        "CONST": "const",
    }

    def __init__(self, out_file: TextIOWrapper) -> None:
        """Create a new output .vm file and prepares it for writing.

        Args:
            out_file (TextIOWrapper): The file to write to
        """
        self.out_file = out_file

    def __del__(self):
        """Close the out_file."""
        self.out_file.close()

    def write_push(self, segment: VirtualSegments, index: int) -> None:
        """Write a VM push command.

        Args:
            segment (VIRTUAL_SEGMENTS): The segment to write
            index (int): The index to write
        """
        self.out_file.write(f"push {self.segment_map[segment]} {index}")

    def write_pop(self, segment: NonConstVirtualSegments, index: int) -> None:
        """Write a VM pop command.

        Args:
            segment (NON_CONST_VIRTUAL_SEGMENTS): The segment to write
            index (int): The index to write
        """
        self.out_file.write(f"pop {self.segment_map[segment]} {index}")

    def write_arithmetic(self, command: Arithmetic) -> None:
        """Write a VM arithmetic-logical command.

        Args:
            command (ARITHMETIC): The command to write
        """
        self.out_file.write(f"{command.lower()}")

    def write_label(self, label: str) -> None:
        """Write a VM label command.

        Args:
            label (str): The label to write
        """
        self.out_file.write(f"label {label}")

    def write_goto(self, label: str) -> None:
        """Write a VM goto command.

        Args:
            label (str): The label to go to
        """
        self.out_file.write(f"goto {label}")

    def write_if(self, label: str) -> None:
        """Write a VM if-goto command.

        Args:
            label (str): The label to go to
        """
        self.out_file.write(f"if-goto {label}")

    def write_call(self, name: str, n_args: int) -> None:
        """Write a VM call command.

        Args:
            name (str): The function name to call
            n_args (int): The number of arguments
        """
        self.out_file.write(f"call {name} {n_args}")

    def write_function(self, name: str, n_locals: int) -> None:
        """Write a VM function command.

        Args:
            name (str): The name of the function to write
            n_locals (int): The number of local variables
        """
        self.out_file.write(f"function {name} {n_locals}")

    def write_return(self) -> None:
        """Write a VM return command."""
        self.out_file.write("return")

    def close(self) -> None:
        """Close the output file."""
        self.out_file.close()
