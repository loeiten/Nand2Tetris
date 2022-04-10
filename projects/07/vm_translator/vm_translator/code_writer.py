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
        """
        Write to the output file the assembly code that implements the given arithmetic command.

        We first dereference the decremented stack pointer.
        This will give us the top of the stack.
        If we do a unary operation we need to increment the stack pointer.
        In this way it will point to the next free address>
        If we do a unary binary operation we need do not need to increment the stack pointer.
        This is because the two topmost element of the stack will be collapsed to one.

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

        # We always need to dereference the decremented stack pointer
        self.file.write(
            f"//{' '*4}Dereferencing the decremeneted stack pointer\n"
            "@SP  // Set A to 0 (side effect: M is set to RAM[0])\n"
            "AM=M-1  // This can be written in two steps\n"
            "        // 1. M=M-1\n"
            "        // 2. A=M\n"
            "        //\n"
            "        // 1. Move stack pointer so that it now points at the top\n"
            "        //    of the stack (set RAM[0] to RAM[0]-1)\n"
            "        // 2. Set A to M-1 (side effect {not used}: M is set to RAM[M-1])\n"
            "D=A  // Set D to RAM[M-1]\n"
        )

        # Decrement the stack pointer for binary operations
        unary_operators = (
            "neg",
            "not",
        )
        if command not in unary_operators:
            # Binary operator
            if command == "add":
                self.file.write(
                    f"//{' '*4}Neg on the stack pointer\n"
                    "@SP  // Set A to 0 (side effect: M is set to RAM[0])\n"
                    "M=-D  // Negate D, and store it to RAM[0]\n"
                )
            elif command == "sub":
                pass
            elif command == "eq":
                pass
            elif command == "lt":
                pass
            elif command == "and":
                pass
            elif command == "or":
                pass

            self.file.write(
                f"//{' '*4}Binary operation: SP points to the correct address\n"
                f"//{' '*6}as we decremented it at the start of this op\n"
            )
        else:
            # Unary operator
            if command == "neg":
                self.file.write(
                    f"//{' '*4}Neg on the stack pointer\n"
                    "@SP  // Set A to 0 (side effect: M is set to RAM[0])\n"
                    "M=-D  // Negate D, and store it to RAM[0]\n"
                )
            elif command == "not":
                self.file.write(
                    f"//{' '*4}Not on the stack pointer\n"
                    "@SP  // Set A to 0 (side effect: M is set to RAM[0])\n"
                    "M=!D  // Not D, and store it to RAM[0]\n"
                )
            # Increment the stack pointer
            self.file.write(
                f"//{' '*4}Increment the stack pointer to point to the first available address\n"
                "@SP  // Set A to 0 (side effect: M is set to RAM[0])\n"
                "M=M+1  // Set RAM[0] to RAM[0]+1\n"
            )

        # In all cases: Add a newline to make the code more readable
        self.file.write("\n")

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
