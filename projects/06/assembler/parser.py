import re
from pathlib import Path

class Parser:
    def __init__(self, path: str) -> None:
        """Open input file to parse.

        Args:
            path (str): Path to file to parse
        """
        self.file = Path(path).resolve().open("r")
        self.current_instruction = None
        # Regexes
        starting_with_comment = r"^\s*(\/\/)+"
        self.ignore_re = re.compile(starting_with_comment)
    
    def __del__(self):
        """Close the file."""
        self.file.close()

    def has_more_lines(self) -> bool:
        """Return if the file has more lines.

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
                self.current_instruction = None
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

    def instruction_type(self) -> str:
        """Return the current instruction type.

        The current instructions are either
        - A_INSTRUCTION for @xxx, where xxx is either a decimal number or a symbol
        - C_INSTRUCTION for dest=comp;jump
        - L_INSTRUCTION for (xxx) where xxx is a symbol

        Returns:
            str: The instruction type
        """
        if self.current_instruction[0] == "@":
            return "A_INSTRUCTION"
        if self.current_instruction[0] == "(":
            return "L_INSTRUCTION"
        return "C_INSTRUCTION"

    def symbol(self) -> str:
        """Return the symbol of the current instruction.

        Should be called only if instruction_type is A_INSTRUCTION or L_INSTRUCTION.

        Returns:
            str: If the current instruction is (xxx), it will return the symbol xxx.
                If the current instruction is @xxx, it will return the symbol or decimal xxx
        """
        cur_symbol = self.current_instruction
        # Strip the parantheses in case of L_INSTRUCTION
        cur_symbol.rstrip(")").lstrip("(") 
        # Strip the @ in case of A_INSTRUCTION
        cur_symbol.lstrip("@") 
        return cur_symbol

    def dest(self) -> str:
        """Return the symbolic dest part of the current C-instruction.

        Should be called only if instruction_type is C_INSTRUCTION.

        Returns:
            str: The symbolic dest part (8 possibilities)
        """
        # NOTE: dest is optional
        if "=" in self.current_instruction:
            cur_dest = self.current_instruction.split("=")[0]
            return cur_dest.replace(" ", "")
        else:
            return ""

    def comp(self) -> str:
        """Return the symbolic comp part of the current C-instruction.

        Should be called only if instruction_type is C_INSTRUCTION.

        Returns:
            str: The symbolic comp part (28 possibilities)
        """
        cur_comp = self.current_instruction
        # NOTE: dest is optional
        if "=" in self.current_instruction:
            cur_comp = cur_comp.split("=")[1]

        # NOTE: jump is optional 
        if ";" in self.current_instruction:
            cur_comp = cur_comp.split(";")[0]

        return cur_comp.replace(" ", "")

    def jump(self) -> str:
        """Return the symbolic jump part of the current C-instruction.

        Should be called only if instruction_type is C_INSTRUCTION.

        Returns:
            str: The symbolic jump part (8 possibilities)
        """
        # NOTE: jump is optional
        if ";" in self.current_instruction:
            cur_jump = self.current_instruction.split(";")[1]
            return cur_jump.replace(" ", "")
        else:
            return ""