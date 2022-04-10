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
            f"//{' '*4}Move stack pointer to top of stack, save content to D\n"
            "@SP  // Set A to 0 (side effect: M is set to content of RAM[0])\n"
            "AM=M-1  // 1. Move stack pointer so that it now points at the\n"
            "        //    top of the stack\n"
            "        //    (set the content of RAM[0] to RAM[0]-1)\n"
            "        // 2. Set A to M-1\n"
            "        //    (side effect: M is set to the content of RAM[M-1])\n"
            "D=M  // 3. Set D to the content of RAM[M-1]\n"
        )

        # Decrement the stack pointer for binary operations
        unary_operators = (
            "neg",
            "not",
        )
        if command not in unary_operators:
            self.file.write(
                f"//{' '*4}Dereference stack pointer -1, save content to A\n"
                "@SP  // Set A to 0\n"
                "     // (side effect: M is set to the content of RAM[0])\n"
                "A=M-1  // Set A to M-1\n"
                "       // (side effect: M is set to the content of RAM[M-1])\n"
            )
            # Binary operator
            if command == "add":
                self.file.write(
                    f"//{' '*4}Add stack pointer and stack pointer -1\n"
                    "M=D+M  // Set the content of stack pointer -1 to D+M\n"
                )
            elif command == "sub":
                self.file.write(
                    f"//{' '*4}Subtract stack pointer and stack pointer -1\n"
                    "M=D-M  // Set the content of stack pointer -1 to D-M\n"
                )
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
