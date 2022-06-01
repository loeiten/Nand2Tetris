"""Module containing the CodeWriter class."""


from pathlib import Path
from typing import Literal


class CodeWriter:
    """Class which writes symbolic Hack assembly code."""

    # See the docstring of write_push_pop for explanation of addresses
    segment_address_map = {
        "local": (
            "   @LCL  // Set A to the base address of the 'local' allocation\n"
            "         // (unused side effect: M is set to content of RAM[LCL])\n"
        ),
        "argument": (
            "   @ARG  // Set A to the base address of the 'argument' allocation\n"
            "         // (unused side effect: M is set to content of RAM[ARG])\n"
        ),
        "this": (
            "   @THIS  // Set A to the base address of the 'this' allocation\n"
            "          // (unused side effect: M is set to content of RAM[THIS])\n"
        ),
        "that": (
            "   @THAT  // Set A to the base address of the 'that' allocation\n"
            "          // (unused side effect: M is set to content of RAM[THAT])\n"
        ),
        # Since "pointer" is allocated from address 3, thus we must add 3 to the index
        "pointer": (
            "   @3  // Set A to the base address of the 'pointer' allocation\n"
            "       // (unused side effect: M is set to content of RAM[3])\n"
        ),
        # Since "temp" is allocated from address 5, thus we must add 5 to the index
        "temp": (
            "   @5  // Set A to the base address of the 'temp' allocation\n"
            "       // (unused side effect: M is set to content of RAM[5])\n"
        ),
    }

    def __init__(self, path: str) -> None:
        """Open the output file/stream and gets ready to write into it.

        Args:
            path (str): Path to file to write to.
        """
        pure_path = Path(path)
        self.file = pure_path.resolve().open("w")

        self.file_name = pure_path.resolve().with_suffix("").name

        # Initialize counters for boolean results
        self._eq_counter = 0
        self._gt_counter = 0
        self._lt_counter = 0

        # Initialize the current function (needed for adding a return label during calls)
        self._current_function = ""

    def set_file_name(self, file_name: str) -> None:
        """Inform the object that the translation of a new VM file has started.

        Args:
            file_name (str): The new file name
        """
        self.file_name = file_name

    def write_init(self) -> None:
        """Write the assembly instructions that effect the bootstrap code that initializes the VM.

        The code generated here myst be placed at the beginning of the generated *.asm file.
        """
        self.write_call(function_name="Sys.init", num_args=0)

    def write_arithmetic(
        self,
        command: Literal["add", "sub", "eq", "gt", "lt", "and", "or", "neg", "not"],
    ) -> None:
        """
        Write to the output file the assembly code that implements the given arithmetic command.

        This is done by:
        1. Dereference the decremented stack pointer to give us the top of the stack
        2. If unary operation: Increment the stack pointer to point to the next free address

        If we do a binary operation we need do not need to increment the stack pointer, since
        the two topmost element of the stack will be collapsed to one.

        NOTE:
        "eq", "gt", "lt" will be treated like LOGICAL operators (working on booleans),
        whereas "and", "or", and "not" not BITWISE operators (working on individual bits).
        The difference is exemplified in
        https://www.tutorialspoint.com/what-are-the-differences-between-bitwise-and-logical-and-operators-in-c-cplusplus

        Also note that the boolean corresponds to the following integers
        True = 11...1 (in base 2) = -1 (in decimal with 2's compliment)
        False = 00...0 (in base 2) = 0 (in decimal)

        Args:
            command (Literal["add", "sub", "eq", "gt", "lt", "and", "or", "neg", "not"]):
                The command to translate into assembly
        """
        # Write the command
        self.file.write(f"// {command}\n")

        # We always need to dereference the decremented stack pointer
        self.file.write(
            f"   //{' '*4}Move stack pointer to top of stack\n"
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
                    "   M=M+D  // Set the content of stack pointer -1 to M+D\n"
                )
            elif command == "sub":
                self.file.write(
                    f"   //{' '*4}Subtract stack pointer and stack pointer -1\n"
                    "   M=M-D  // Set the content of stack pointer -1 to M-D\n"
                )
            elif command in ("eq", "gt", "lt"):
                # mypy does not notice that the command above restricts the input of `command`
                self._write_eq_gt_lt_result(command)  # type: ignore
            elif command == "and":
                self.file.write(
                    f"   //{' '*4}Logic stack pointer AND stack pointer -1\n"
                    "   M=M&D  // Set the content of stack pointer -1 to M&D\n"
                )
            elif command == "or":
                self.file.write(
                    f"   //{' '*4}Logic stack pointer OR stack pointer -1\n"
                    "   M=M|D  // Set the content of stack pointer -1 to M|D\n"
                )

            self.file.write(
                f"//{' '*4}Binary operation: SP points to the correct address\n"
                f"//{' '*4}as we decremented it at the start of this op\n"
            )
        else:
            # Unary operator
            if command == "neg":
                self.file.write(
                    f"   //{' '*4}Neg on the stack pointer\n"
                    "   @SP  // Set A to 0 (side effect: M is set to RAM[0])\n"
                    "   A=M  // Dereference\n"
                    "   M=-D  // Negate D, and store it to RAM[RAM[0]]\n"
                )
            elif command == "not":
                self.file.write(
                    f"   //{' '*4}Not on the stack pointer\n"
                    "   @SP  // Set A to 0 (side effect: M is set to RAM[0])\n"
                    "   A=M  // Dereference\n"
                    "   M=!D  // Not D, and store it to RAM[RAM[0]]\n"
                )
            # Increment the stack pointer
            self.file.write(
                f"   //{' '*4}Increment the stack pointer to point to the first available address\n"
                "   @SP  // Set A to 0 (side effect: M is set to RAM[0])\n"
                "   M=M+1  // Set RAM[0] to RAM[0]+1\n"
            )

        # In all cases: Add 2 newlines to make the code more readable
        self.file.write("\n" * 2)

    def _write_eq_gt_lt_result(self, command: Literal["eq", "gt", "lt"]):
        """Write the result of "eq", "gt" and "lt".

        Args:
            command (Literal["eq", "gt", "lt"]): Command to write result of
        """
        command_counter = {
            "eq": self._eq_counter,
            "lt": self._lt_counter,
            "gt": self._gt_counter,
        }
        jump_statement = {
            "eq": "JEQ",
            "lt": "JLT",
            "gt": "JGT",
        }
        counter = command_counter[command]
        jump = jump_statement[command]
        self.file.write(
            f"   //{' '*4}Check for '{command}'\n"
            "   D=M-D  // By subtracting M and D we can check for equality\n"
            f"   @{command.upper()}_{counter}\n"
            f"   D;{jump}  // Jump to label above if true\n"
            "   @SP  // Select the current stack pointer (first non-free address)\n"
            "   A=M-1  // Dereference previous stack pointer\n"
            "   M=0  // Condition checked for was false\n"
            f"   @END_{command.upper()}_{counter}\n"
            "   0;JMP  // Always jump to the end\n"
            f"({command.upper()}_{counter})\n"
            "   @SP  // Select the current stack pointer (first non-free address)\n"
            "   A=M-1  // Dereference previous stack pointer\n"
            "   M=-1  // Condition checked for was true\n"
            f"(END_{command.upper()}_{counter})\n"
        )
        # Increment counter
        setattr(self, f"_{command}_counter", getattr(self, f"_{command}_counter") + 1)
        counter += 1

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
        temp - 5-12
        general purpose registers (not used by VM) - 13-15
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
                - push static i => addr = 16 + i, *SP=*addr, SP++ (use @file_name.i)
                - pop static i => addr = 16 + i, SP--, *addr=*SP (use @file_name.i)
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
        command_map = {"C_PUSH": "push", "C_POP": "pop"}
        self.file.write(f"// {command_map[command]} {segment} {index}\n")

        # Obtain the address
        self._write_address(command=command, segment=segment, index=index)

        if command == "C_PUSH":
            # Push from a virtual allocation to the stack

            if segment not in ("constant", "static"):
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

            # We here take advantage of a trick that both value and address can be stored in a
            # variable
            # This is perhaps less readable, but more efficient

            # An alternative approach:
            # //    Store address to general purpose register
            # @13  // General purpose register
            # M=D  // Store the address to the general purpose register
            # //    Get the memory address to obtain the memory from
            # @SP  // Set A to 0 (side effect: M is set to content of RAM[0])
            # M=M-1  // Decrement the content of RAM[0]
            # A=M  // Set the address to the memory address RAM[0] is pointing to
            # D=M  // Store the content of the address pointed to by RAM[0]
            # //    Store the content of the stack pointer to the address stored in @13
            # @13 // Select the general purpose register
            # A=M // Set the address to the address pointed to by 13
            # M=D // Store D into the address pointed to by 13

            # We must always decrement the stack pointer before a pop
            self.file.write(
                f"   //{' '*4}Add the top of the stack to D, so that D holds RAM[SP] + addr\n"
                "   @SP  // Set A to 0 (side effect: M is set to content of RAM[0])\n"
                "   AM=M-1  // Decrement the content of RAM[0] and set this to the new address\n"
                "           // Side effect: M is set to content of RAM[RAM[0]-1]\n"
                "   D=D+M  // RHS: D holds the 'address', M holds the content of RAM[RAM[0]-1]\n"
                f"   //{' '*4}Select the address to pop to and store D\n"
                "   A=D-M  // A <- ('addr' + content of RAM[RAM[0]-1]) - content of RAM[RAM[0]-1]\n"
                "          // Side effect: M is set to the content of the 'address'\n"
                "   M=D-A  // M <- ('address; + content of RAM[RAM[0]-1]) - 'address'\n"
            )

        # In all cases: Add 2 newlines to make the code more readable
        self.file.write("\n" * 2)

    def _write_address(
        self,
        command: Literal["C_PUSH", "C_POP"],
        segment: Literal[
            "local", "argument", "this", "that", "constant", "static", "pointer", "temp"
        ],
        index: int,
    ) -> None:
        """
        Write to the file the part where the address is obtained.

        See "Pseudocode" in write_push_pop for details.

        Args:
            command (Literal["C_PUSH", "C_POP"]): The command to translate into assembly
            segment (Literal["local", "argument", "this", "that", "constant", "static", "pointer",
            "temp"]):
                Which virtual memory segment to push from/pop to
            index (int): Segment index to push from/pop to
        """
        if segment != "static":
            self.file.write(
                f"   //{' '*4}Get the memory address to obtain the memory from\n"
                f"   @{index}  // Set A to 'index'\n"
                "             // (unused side effect: M is set to content of RAM['index'])\n"
                f"   D=A  // Store the index to the D register\n"
            )
        else:
            self.file.write(
                f"   //{' '*4}Get the static memory address\n"
                f"   @{self.file_name}.{index}  // Set A to the static memory\n"
            )
            if command == "C_PUSH":
                self.file.write(
                    f"     // (side effect: M is set to RAM['{self.file_name}.{index}'])\n"
                    f"   D=M  // Store M to the D register\n"
                )
            elif command == "C_POP":
                self.file.write(
                    f"     // (unused side effect: M is set to RAM['{self.file_name}.{index}'])\n"
                    f"   D=A  // Store the address to the D register\n"
                )

        if segment not in ("constant", "static"):
            # NOTE: if segment != "constant": The address already stored to A, and we
            #       don't need to add a base address to get what we need
            self.file.write(self.segment_address_map[segment])

            # Constant is constant, we don't need to add anything to get what we need
            if command == "C_PUSH":
                if segment in ("local", "argument", "this", "that"):
                    self.file.write(
                        "   A=D+M  // Set A to the desired address\n"
                        "          // (side effect: M is set to content of RAM[D+M])\n"
                    )
                elif segment in ("static", "temp", "pointer"):
                    self.file.write(
                        "   A=D+A  // Set A to the desired address\n"
                        "          // (side effect: M is set to content of RAM[D+A])\n"
                    )

            elif command == "C_POP":
                if segment in ("local", "argument", "this", "that"):
                    self.file.write(
                        "   D=D+M  // Set D to index (D) + base address (M)\n"
                    )
                elif segment in ("static", "temp", "pointer"):
                    self.file.write(
                        "   D=D+A  // Set D to index (D) + constant address (A)\n"
                    )

    def write_label(self, label: str) -> None:
        """Write assembly code that effects the `label` command.

        Args:
            label (str): The label to effect
        """
        self.file.write(f"({label})\n")
        # Add 2 newlines to make the code more readable
        self.file.write("\n" * 2)

    def write_goto(self, label: str) -> None:
        """Write assembly code that effects the `goto` command.

        Args:
            label (str): The label to go to
        """
        self.file.write(
            f"// goto {label}\n"
            f"   @{label}  // Select label to jump to\n"
            f"   0;JMP  // Unconditional jump\n"
        )
        # Add 2 newlines to make the code more readable
        self.file.write("\n" * 2)

    def write_if(self, label: str) -> None:
        """Write assembly code that effects the `if-goto` command.

        Args:
            label (str): The label to go to
        """
        self.file.write(
            f"// if-goto {label}\n"
            "   @SP  // Set A to 0 (side effect: M is set to content of RAM[0])\n"
            "   AM=M-1  // Pop SP and set A to the first non-free location in the stack"
            "          // (side effect: M is set to content of RAM[RAM[0]-1])\n"
            "   D=M  // Store the content of RAM[RAM[0]-1] to D\n"
            f"   @{label}  // Select label to jump to\n"
            f"   D;JNE  // Jump if D != 0\n"
        )
        # Add 2 newlines to make the code more readable
        self.file.write("\n" * 2)

    def write_function(self, function_name: str, num_vars: int) -> None:
        """Write assembly code that effects the `function` command.

        Args:
            function_name (str): Name of the function
            num_vars (int): Number of local variables in the function
        """
        # Update the current function (needed for adding a return label during calls)
        self._current_function = function_name
        self.file.write(
            f"// function {function_name} {num_vars}\n"
            f"({function_name})\n"
            f"   //{' '*4}Initialise the local variables\n"
        )
        for num_var in range(num_vars):
            self.file.write(
                f"   //{' '*4}Initialize local variable {num_var}\n"
                f"   @{num_var}  // Set A to the number LCL should be incremented to\n"
                "   D=A  // Store this number to D\n"
                "   @LCL  // Set A to 1 (side effect: M is set to content of RAM[1])\n"
                "   A=M+D  // Set A the address to the address pointed to by LCL + D\n"
                "          // (side effect: M is set to content of RAM[RAM[1] + D])\n"
                "   M=0  // Set the dereferenced address to 0\n"
                f"   //{' '*4}Update the stack pointer\n"
                "   @SP  // Set A to 0 (side effect: M is set to content of RAM[0])\n"
                "   M=M+1  // Increment the stack pointer\n"
            )

        # Add 2 newlines to make the code more readable
        self.file.write("\n" * 2)

    def write_call(self, function_name: str, num_args: int) -> None:
        """Write assembly code that effects the `call` command.

        Args:
            function_name (str): Name of the function
            num_args (int): Number of arguments passed to the function
        """
        self.file.write(
            f"// call {function_name} {num_args}\n"
            f"   //{' '*4}Push the return address to the stack\n"
        )
        self._push_address_to_stack(f"{self._current_function}$return", label=True)
        self.file.write(f"   //{' '*4}Push LCL of the caller to the stack\n")
        self._push_address_to_stack("LCL")
        self.file.write(f"   //{' '*4}Push ARG of the caller to the stack\n")
        self._push_address_to_stack("ARG")
        self.file.write(f"   //{' '*4}Push THIS of the caller to the stack\n")
        self._push_address_to_stack("THIS")
        self.file.write(f"   //{' '*4}Push THAT of the caller to the stack\n")
        self._push_address_to_stack("THAT")
        self.file.write(
            f"   //{' '*4}Reposition ARG to ARG = SP-5-nArgs\n"
            f"   //{' '*8}Store how much to subtract to D\n"
            "   @5  // Set A to 5 (M unused)\n"
            "   D=A  // Store 5 to D\n"
            f"   @{num_args}  // Set A to the number of arguments (M unused)\n"
            "   D=D+A  // Store 5 + number of arguments to D\n"
            "   @SP  // Set A to the SP, M is set to the content of RAM[SP]\n"
            "   D=M-D  // SP-5-nArgs\n"
            f"   @ARG  // Set A to point to ARG (M is pointing to RAM[ARG])\n"
            "   M=D  // Let ARG point to SP-5-nArgs\n"
            f"   //{' '*4}Reposition LCL to LCL = SP\n"
            "   @SP  // Set A to the SP, M is set to the content of RAM[SP]\n"
            "   D=M  // Set D to the address which SP is pointing to\n"
            "   @LCL  // Set A to LCL, M is set to the content of RAM[LCL]\n"
            "   M=D  // Let LCL point to SP\n"
            f"   //{' '*4}Transfers control to the called function: goto {function_name}\n"
            f"   @{function_name}\n"
            "   0;JMP\n"
            f"   //{' '*4}Make the return label\n"
            f"({self._current_function}$return)\n"
        )

        # Add 2 newlines to make the code more readable
        self.file.write("\n" * 2)

    def _push_address_to_stack(self, address: str, label: bool = False) -> None:
        """Push an address to the stack.

        Args:
            address (str): Address to be pushed
            label (bool): If the address is a label
        """
        self.file.write(f"    @{address}\n")

        if label:
            self.file.write("    D=A  // Store the current address to D\n")
        else:
            self.file.write(
                f"    D=M  // Store the address pointed to by {address} to D\n"
            )

        self.file.write(
            "    @0  // Set the address to the address of the next free position on the stack\n"
            "        // Side effect: M is set to the content of RAM[0]\n"
            "    A=M  // Let the address point to the next free position in the stack\n"
            f"    M=D  // Store the value of {address}\n"
            f"   //{' '*8}Increment the SP\n"
            "    @0  // Set the address to the address of the next free position on the stack\n"
            "        // Side effect: M is set to the content of RAM[0]\n"
            "    M=M+1  // Increment the SP\n"
        )

    def write_return(self) -> None:
        """Write assembly code that effects the `return` command."""
        self.file.write(
            "// return\n"
            f"   //{' '*4}Store endFrame as a temporary variable\n"
            "   @LCL  // Get the local address (side effect: M is set to the content of RAM[LCL])\n"
            "   D=M  // Store the address of LCL to D\n"
            "   @13  // Select the first temp address\n"
            "       // (side effect: M is set to content of RAM[13])\n"
            "   M=D  // Store the previous LCL address to tmp\n"
            f"   //{' '*4}Store retAddr as a temporary variable\n"
            "   @5  // Select the number 5\n"
            "   A=D-A  // Get the content of RAM[endFrame - 5]\n"
            "   D=M  // Store the content of endFrame - 5 to D\n"
            "   @14  // Select the second temp address\n"
            "       // (side effect: M is set to content of RAM[13])\n"
            "   M=D  // Store the return address to tmp\n"
            f"   //{' '*4}Pop the return value for the caller to ARG\n"
            "   @SP  // Set A to 0 (side effect: M is set to content of RAM[0])\n"
            "   A=M-1  // Decrement the content of RAM[0]\n"
            "          // Side effect: M is set to content of RAM[RAM[0]-1]\n"
            "   D=M  // Store the return value to D\n"
            "   @ARG  // Get the ARG address (side effect: M is set to the content of RAM[ARG])\n"
            "   A=M  // Dereference ARG (side effect: M is set to the content of RAM[RAM[ARG]])\n"
            "   M=D  // Set the value ARG is pointing on to the return value\n"
            f"   //{' '*4}Reposition SP of the caller\n"
            "   @ARG  // Get the ARG address\n"
            "         // (side effect: M is set to the content of RAM[ARG])\n"
            "   D=M+1  // Store the address + 1 to D\n"
            "   @SP  // Set A to 0 (side effect: M is set to content of RAM[0])\n"
            "   M=D  // Set the SP to ARG + 1\n"
            f"   //{' '*4}Restore THAT of the caller\n"
            "   @13  // Get the endFrame address (side effect: M is set to content of RAM[13])\n"
            "   A=M-1  // THAT should be set to the content of endFrame-1\n"
            "   D=M  // Store the content of endFrame-1\n"
            "   @THAT  // Get the THAT address (side effect: M is set to content of RAM[THAT])\n"
            "   M=D  // Store the content of endFrame-1 to THAT\n"
            f"   //{' '*4}Restore THIS of the caller\n"
            "   @2  // Get the number 2 (unused side effect: M is set to the content of RAM[2])\n"
            "   D=A  // Store 2 to D\n"
            "   @13  // Get the endFrame address (side effect: M is set to content of RAM[13])\n"
            "   A=M-D  // THIS should be set to the content of endFrame-2\n"
            "   D=M  // Store the content of endFrame-2\n"
            "   @THIS  // Get the THIS address (side effect: M is set to content of RAM[THIS])\n"
            "   M=D  // Store the content of endFrame-2 to THIS\n"
            f"   //{' '*4}Restore ARG of the caller\n"
            "   @3  // Get the number 3 (unused side effect: M is set to the content of RAM[3])\n"
            "   D=A  // Store 3 to D\n"
            "   @13  // Get the endFrame address (side effect: M is set to content of RAM[13])\n"
            "   A=M-D  // ARG should be set to the content of endFrame-3\n"
            "   D=M  // Store the content of endFrame-3\n"
            "   @ARG  // Get the ARG address (side effect: M is set to content of RAM[ARG])\n"
            "   M=D  // Store the content of endFrame-3 to ARG\n"
            f"   //{' '*4}Restore LCL of the caller\n"
            "   @4  // Get the number 4 (unused side effect: M is set to the content of RAM[4])\n"
            "   D=A  // Store 4 to D\n"
            "   @13  // Get the endFrame address (side effect: M is set to content of RAM[13])\n"
            "   A=M-D  // LCL should be set to the content of endFrame-4\n"
            "   D=M  // Store the content of endFrame-4\n"
            "   @LCL  // Get the LC address (side effect: M is set to content of RAM[LCL])\n"
            "   M=D  // Store the content of endFrame-4 to LCL\n"
            f"   //{' '*4}Jump to the retAddr\n"
            "   @14  // Select the second temp address (where we stored retAddr)\n"
            "   A=M  // Get the content of RAM[14]\n"
            "   0;JMP\n"
        )

        # Add 2 newlines to make the code more readable
        self.file.write("\n" * 2)

    def close(self) -> None:
        """Close the output file."""
        self.file.close()
