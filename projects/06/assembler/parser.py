class Parser:
    def __init__(self, path: str) -> None:
        """Open input file to parse.

        Args:
            path (str): Path to file to parse
        """
        self.current_instruction = None
        pass

    def has_more_lines(self) -> bool:
        """Return if the file has more lines.

        Returns:
            bool: True if the file has more lines
        """
        pass

    def advance(self) -> None:
        """Advance to the next instruction.

        Will populate self.current_instruction, and skip over whitespace and comments.

        This method should be called only if has_more_lines is true.
        """
        pass

    def instruction_type(self) -> str:
        """Return the current instruction type.

        The current instructions are either
        - A_INSTRUCTION for @xxx, where xxx is either a decimal number or a symbol
        - C_INSTRUCTION for dest=comp;jump
        - L_INSTRUCTION for (xxx) where xxx is a symbol
        

        Returns:
            str: The instruction type
        """
        pass

    def symbol(self) -> str:
        """Return the symbol of the current instruction.

        Should be called only if instruction_type is A_INSTRUCTION or L_INSTRUCTION.

        Returns:
            str: If the current instruction is (xxx), it will return the symbol xxx.
                If the current instruction is @xxx, it will return the symbol or decimal xxx
        """
        pass

    def dest(self) -> str:
        """Return the symbolic dest part of the current C-instruction.

        Should be called only if instruction_type is C_INSTRUCTION.

        Returns:
            str: The symbolic dest part (8 possibilities)
        """
        pass

    def comp(self) -> str:
        """Return the symbolic comp part of the current C-instruction.

        Should be called only if instruction_type is C_INSTRUCTION.

        Returns:
            str: The symbolic comp part (28 possibilities)
        """
        pass

    def jump(self) -> str:
        """Return the symbolic jump part of the current C-instruction.

        Should be called only if instruction_type is C_INSTRUCTION.

        Returns:
            str: The symbolic jump part (8 possibilities)
        """
        pass