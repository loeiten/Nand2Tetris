"""Module containing the Code class."""


class Code:
    """Class mapping predefined symbols to binary strings."""

    dest_dict = {
        "": "000",
        "null": "000",
        "M": "001",
        "D": "010",
        "DM": "011",
        "MD": "011",
        "A": "100",
        "AM": "101",
        "MA": "101",
        "AD": "110",
        "DA": "110",
        "ADM": "111",
        "AMD": "111",
        "DAM": "111",
        "DMA": "111",
        "MAD": "111",
        "MDA": "111",
    }
    comp_dict = {
        "0": "101010",
        "1": "111111",
        "-1": "111010",
        "D": "001100",
        "A": "110000",
        "M": "110000",
        "!D": "001101",
        "!A": "110001",
        "!M": "110001",
        "-D": "001111",
        "-A": "110011",
        "-M": "110011",
        "D+1": "011111",
        "A+1": "110111",
        "M+1": "110111",
        "D-1": "001110",
        "A-1": "110010",
        "M-1": "110010",
        "D+A": "000010",
        "D+M": "000010",
        "D-A": "010011",
        "D-M": "010011",
        "A-D": "000111",
        "M-D": "000111",
        "D&A": "000000",
        "A&D": "000000",
        "D&M": "000000",
        "M&D": "000000",
        "D|A": "010101",
        "A|D": "010101",
        "D|M": "010101",
        "M|D": "010101",
    }
    jump_dict = {
        "": "000",
        "null": "000",
        "JGT": "001",
        "JEQ": "010",
        "JGE": "011",
        "JLT": "100",
        "JNE": "101",
        "JLE": "110",
        "JMP": "111",
    }

    def dest(self, string: str) -> str:
        """Return the binary code of the dest mnemonic.

        Args:
            string (str): A dest mnemonic.

        Returns:
            str: The corresponding binary code, 3 bits
        """
        return self.dest_dict[string]

    def comp(self, string: str) -> str:
        """Return the binary code of the comp mnemonic.

        Args:
            string (str): A comp mnemonic.

        Returns:
            str: The corresponding binary code, 7 bits
        """
        a_bit = "1" if "M" in string else "0"
        return a_bit + self.comp_dict[string]

    def jump(self, string: str) -> str:
        """Return the binary code of the jump mnemonic.

        Args:
            string (str): A jump mnemonic.

        Returns:
            str: The corresponding binary code, 3 bits
        """
        return self.jump_dict[string]
