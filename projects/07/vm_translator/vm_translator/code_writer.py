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
        pure_path = Path(path)
        self.file = pure_path.resolve().open("r")
        self.file_name = pure_path.with_suffix("").name

        # Initialize the less than and greater than counter
        self._lt_counter = 0
        self._gt_counter = 0

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
        # Write the command
        self.file.write(f"// {command}\n")

        # We always need to dereference the decremented stack pointer
        self.file.write(
            f"   //{' '*4}Move stack pointer to top of stack, save content to D\n"
            "   @SP  // Set A to 0 (side effect: M is set to content of RAM[0])\n"
            "   AM=M-1  // 1. Move stack pointer so that it now points at the\n"
            "           //    top of the stack\n"
            "           //    (set the content of RAM[0] to RAM[0]-1)\n"
            "           // 2. Set A to M-1\n"
            "           //    (side effect: M is set to the content of RAM[M-1])\n"
            "   D=M  // 3. Set D to the content of RAM[M-1]\n"
        )

        # Decrement the stack pointer for binary operations
        unary_operators = (
            "neg",
            "not",
        )
        if command not in unary_operators:
            self.file.write(
                f"   //{' '*4}Dereference stack pointer -1, save content to A\n"
                "   @SP  // Set A to 0\n"
                "        // (side effect: M is set to the content of RAM[0])\n"
                "   A=M-1  // Set A to M-1\n"
                "          // (side effect: M is set to the content of RAM[M-1])\n"
            )
            # Binary operator
            if command == "add":
                self.file.write(
                    f"   //{' '*4}Add stack pointer and stack pointer -1\n"
                    "   M=D+M  // Set the content of stack pointer -1 to D+M\n"
                )
            elif command == "sub":
                self.file.write(
                    f"   //{' '*4}Subtract stack pointer and stack pointer -1\n"
                    "   M=D-M  // Set the content of stack pointer -1 to D-M\n"
                )
            elif command == "eq":
                self.file.write(
                    f"   //{' '*4}Check for equality\n"
                    "   M=D-M  // Set the content of stack pointer -1 to D-M\n"
                    "   D=0  // Set D to 0\n"
                    "   M=D|M  // If M is non-zero, we have inequality\n"
                    "          // OR(0, M) is 1 only if M is non-zero\n"
                    "   M=!M  // The new M will be 1 (true) only if the previous was 0\n"
                )
            elif command == "gt":
                self.file.write(
                    f"   //{' '*4}Check for less than\n"
                    "   M=D-M  // Set the content of stack pointer -1 to D-M\n"
                    "   D=A  // Store the current stack pointer address to D\n"
                    "   @CUR_SP_ADDRESS  // Set A to CUR_SP_ADDRESS\n"
                    "                    // (side effect: M is set to the content of RAM[A])\n"
                    "   M=D  // Store the current address to a register\n"
                    "   A=M  // Set A to M\n"
                    "        // (side effect: M is set to the content of RAM[A].\n"
                    "        //  This is now equal to *SP - *(SP-1))\n"
                    "   D=M  // Set D to the content of stack pointer - 1\n"
                    f"   @GT_TRUE_{self._gt_counter}\n"
                    f"   D;JGT  // Jump to GT_TRUE_{self._gt_counter} if D<0\n"
                    f"   //{' '*8}If D is not greater than 0, continue on this branch:\n"
                    "   @CUR_SP_ADDRESS  // Retrieve the memory address of stack pointer -1\n"
                    "   A=M  // Retrieve the memory address of stack pointer -1\n"
                    "        // (side effect: M is set to the content of RAM[M-1])\n"
                    "   M=0  // Set the memory of stack pointer -1 to false\n"
                    f"   @GT_TRUE_{self._gt_counter}_END\n"
                    f"   0;JMP  // Unconditionally jump to GT_TRUE_{self._gt_counter}_END\n"
                    "\n"
                    f"(GT_TRUE_{self._gt_counter})\n"
                    "   @CUR_SP_ADDRESS  // Retrieve the memory address of stack pointer -1\n"
                    "   A=M  // Retrieve the memory address of stack pointer -1\n"
                    "        // (side effect: M is set to the content of RAM[M-1])\n"
                    "   M=1  // Set the memory of stack pointer -1 to true\n"
                    "\n"
                    f"(GT_TRUE_{self._gt_counter}_END)\n"
                )
                self._gt_counter += 1
            elif command == "lt":
                self.file.write(
                    f"   //{' '*4}Check for less than\n"
                    "   M=D-M  // Set the content of stack pointer -1 to D-M\n"
                    "   D=A  // Store the current stack pointer address to D\n"
                    "   @CUR_SP_ADDRESS  // Set A to CUR_SP_ADDRESS\n"
                    "                    // (side effect: M is set to the content of RAM[A])\n"
                    "   M=D  // Store the current address to a register\n"
                    "   A=M  // Set A to M\n"
                    "        // (side effect: M is set to the content of RAM[A].\n"
                    "        //  This is now equal to *SP - *(SP-1))\n"
                    "   D=M  // Set D to the content of stack pointer - 1\n"
                    f"   @LT_TRUE_{self._lt_counter}\n"
                    f"   D;JLT  // Jump to LT_TRUE_{self._lt_counter} if D<0\n"
                    f"   //{' '*8}If D is not less than 0, continue on this branch:\n"
                    "   @CUR_SP_ADDRESS  // Retrieve the memory address of stack pointer -1\n"
                    "   A=M  // Retrieve the memory address of stack pointer -1\n"
                    "        // (side effect: M is set to the content of RAM[M-1])\n"
                    "   M=0  // Set the memory of stack pointer -1 to false\n"
                    f"   @LT_TRUE_{self._lt_counter}_END\n"
                    f"   0;JMP  // Unconditionally jump to LT_TRUE_{self._lt_counter}_END\n"
                    "\n"
                    f"(LT_TRUE_{self._lt_counter})\n"
                    "   @CUR_SP_ADDRESS  // Retrieve the memory address of stack pointer -1\n"
                    "   A=M  // Retrieve the memory address of stack pointer -1\n"
                    "        // (side effect: M is set to the content of RAM[M-1])\n"
                    "   M=1  // Set the memory of stack pointer -1 to true\n"
                    "\n"
                    f"(LT_TRUE_{self._lt_counter}_END)\n"
                )
                self._lt_counter += 1
            elif command == "and":
                self.file.write(
                    f"   //{' '*4}Logic stack pointer AND stack pointer -1\n"
                    "   M=D&M  // Set the content of stack pointer -1 to D&M\n"
                )
            elif command == "or":
                self.file.write(
                    f"   //{' '*4}Logic stack pointer OR stack pointer -1\n"
                    "   M=D|M  // Set the content of stack pointer -1 to D|M\n"
                )

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

        # In all cases: Add 2 newlines to make the code more readable
        self.file.write("\n" * 2)

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

        Memory mapping:
        SP - 0 - points to the next free stack address
        LCL - 1
        ARG - 2
        THIS - 3
        THAT - 4
        temp - 5-17
        static - 16-255
        stack - 256-2047
        pointer - 3-4 - pointer 0 => RAM[3], pointer 1 => RAM[4]
        general purpose registers - 13-15
        constant i => RAM[i]
        segment i => RAM[*segment_pointer + i]

        NOTE: The base address of the "local", "argument", "this" and "that" allocations are kept
              the segment pointers LCL, ARG, THIS, THAT
              The standard mapping will be extended in the next project

        Pseudocode:
            - If segment == {local, argument, this, that}
                - push segment i => addr = segmentPointer + i, *SP=*addr, SP++
                - pop segment i => addr = segmentPointer + i, SP--, *addr=*SP
            - If segment == constant
                - push constant i => *SP=i, SP++
                - No pop command
            - If segment == static
                - push static i => addr = 16 + i, *SP=*addr, SP++ (use @filename.i)
                - pop static i => addr = 16 + i, SP--, *addr=*SP (use @filename.i)
            - If segment == pointer
                - push pointer 0/1 => addr = 3 + 0/1, *SP=*addr, SP++
                - pop pointer 0/1 => addr = 3 + 0/1, SP--, *addr=*SP
            - If segment == temp
                - push temp i => addr = 5 + i, *SP=*addr, SP++
                - pop temp i => addr = 5 + i, SP--, *addr=*SP

        Args:
            command (Literal["C_PUSH", "C_POP"]): The command to translate into assembly
            segment (Literal["local", "argument", "this", "that", "constant", "static", "pointer",
            "temp"]):
                Which virtual memory segment to push from/pop to
            index (int): Segment index to push from/pop to
        """
        # Write the command
        self.file.write(f"// {command}\n")

        if command == "C_PUSH":
            # Push from a virtual allocation to the stack

            # Obtain the address
            self._write_address(segment=segment, index=index)
            if segment != "constant":
                self.file.write("   D=M  // Store the content of RAM[D+A] to D\n")

            # Set the new content of the SP, and increment the SP
            self.file.write(
                f"   //{' '*4}Set the content of the address the SP is pointing to to D\n"
                "   @SP  // Set A to 0 (side effect: M is set to content of RAM[0])\n"
                "   A=M  // Set A to RAM[0] (side effect: M is set to content of RAM[RAM[0]])\n"
                "   M=D  // Set the content of RAM[RAM[0]] to D\n"
                f"   //{' '*4}Increment the stack pointer to the next free memory address\n"
                "   @SP  // Set A to 0 (side effect: M is set to content of RAM[0])\n"
                "   M=M+1  // Increment the content of RAM[0]\n"
            )
        elif command == "C_POP":
            # Pop from the stack to a virtual allocation

            # We must always decrement the stack pointer before a pop
            self.file.write(
                f"   //{' '*4}Decrement the stack pointer to the first non-free memory address\n"
                "   @SP  // Set A to 0 (side effect: M is set to content of RAM[0])\n"
                "   M=M-1  // Decrement the content of RAM[0]\n"
                f"   //{' '*4}Store the content of the stack pointer to a variable\n"
                "   D=M  // Store the content of SP to D\n"
                "   @SP_CONTENT  // Set A to the SP_CONTENT variable\n"
                "                // (side effect: M is set to content of RAM[SP_CONTENT])\n"
                "   M=D  // Set the content of RAM[SP_CONTENT] to D\n"
            )

            # Obtain the address
            self._write_address(segment=segment, index=index)

            # Set the M of the address to the current stack pointer
            self.file.write(
                f"   //{' '*4}Store the current address to the ADDR variable\n"
                "   D=A  // Store the current address to D\n"
                "   @ADDR  // Set A to the ADDR variable\n"
                "          // (side effect: M is set to content of RAM[ADDR])\n"
                "   M=D  // Store the address to RAM[ADDR]\n"
                f"   //{' '*4}Retrieve the content of the stack pointer\n"
                "   @SP_CONTENT  // Set A to the SP_CONTENT variable\n"
                "                // (side effect: M is set to content of RAM[SP_CONTENT])\n"
                "   D=M  // Store the content of the stack pointer to D \n"
                f"   //{' '*4}Store the content of the stack pointer to the content of ADDR\n"
                "   @ADDR  // Set A to the ADDR variable\n"
                "          // (side effect: M is set to content of RAM[ADDR])\n"
                "   M=D  // Store the content of the stack pointer to the ADDR memory\n"
            )

        # In all cases: Add 2 newlines to make the code more readable
        self.file.write("\n" * 2)

    def _write_address(
        self,
        segment: Literal[
            "local", "argument", "this", "that", "constant", "static", "pointer", "temp"
        ],
        index: int,
    ) -> None:
        """
        Write to the file the part where the address is obtained.

        See "Pseudocode" in write_push_pop for details.

        Args:
            segment (Literal["local", "argument", "this", "that", "constant", "static", "pointer",
            "temp"]):
                Which virtual memory segment to push from/pop to
            index (int): Segment index to push from/pop to
        """
        self.file.write(
            f"   //{' '*4}Get the memory address to obtain the memory from\n"
            f"   @{index}  // Set A to 'index'\n"
            "             // (unused side effect: M is set to content of RAM['index'])\n"
            f"   D=A  // Store the index to the D register\n"
        )

        if segment == "local":
            self.file.write(
                "   @LCL  // Set A to the base address of the 'local' allocation\n"
                "         // (unused side effect: M is set to content of RAM[LCL])\n"
            )
        elif segment == "argument":
            self.file.write(
                "   @ARG  // Set A to the base address of the 'argument' allocation\n"
                "         // (unused side effect: M is set to content of RAM[ARG])\n"
            )
        elif segment == "this":
            self.file.write(
                "   @THIS  // Set A to the base address of the 'this' allocation\n"
                "         // (unused side effect: M is set to content of RAM[THIS])\n"
            )
        elif segment == "that":
            self.file.write(
                "   @THAT  // Set A to the base address of the 'that' allocation\n"
                "         // (unused side effect: M is set to content of RAM[THAT])\n"
            )
        elif segment == "constant":
            self.file.write("   D=A  // Store the address to D\n")
        elif segment == "static":
            # Since "static" is allocated from address 16, thus we must add 16 to the index
            self.file.write(
                "   @16  // Set A to the base address of the 'static' allocation\n"
                "         // (unused side effect: M is set to content of RAM[16])\n"
            )
        elif segment == "pointer":
            # Since "pointer" is allocated from address 3, thus we must add 3 to the index
            self.file.write(
                "   @3  // Set A to the base address of the 'pointer' allocation\n"
                "         // (unused side effect: M is set to content of RAM[3])\n"
            )

        if segment != "constant":
            # Constant is constant, we don't need to add anything to get what we need
            self.file.write(
                "   A=D+A  // Set A to the desired address\n"
                "          // (side effect: M is set to content of RAM[D+A])\n"
            )

    def close(self) -> None:
        """Close the output file."""
        self.file.close()
