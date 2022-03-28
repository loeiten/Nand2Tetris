"""Module containing SymbolTable class."""


class SymbolTable:
    """Class for manipulating the symbol table."""

    def __init__(self) -> None:
        """Create a new empty symbol table."""
        self._next_available_entry = 16
        self.symbol_table = {
            "R0": 0,
            "R1": 1,
            "R2": 2,
            "R3": 3,
            "R4": 4,
            "R5": 5,
            "R6": 6,
            "R7": 7,
            "R8": 8,
            "R9": 9,
            "R10": 10,
            "R11": 11,
            "R12": 12,
            "R13": 13,
            "R14": 14,
            "R15": 15,
            "SCREEN": 16384,
            "KBD": 24576,
            "SP": 0,
            "LCL": 1,
            "ARG": 2,
            "THIS": 3,
            "THAT": 4,
        }

    def add_entry(self, symbol: str, address: int) -> None:
        """Add <symbol, address> to the table.

        Args:
            symbol (str): The symbol to add to the table.
            address (int): The corresponding address.
        """
        self.symbol_table[symbol] = address

    def contains(self, symbol: str) -> bool:
        """Check if the symbol table contains the symbol.

        Args:
            symbol (str): The symbol to query.

        Returns:
            bool: True if the symbol is contained.
        """
        return symbol in self.symbol_table

    def get_address(self, symbol: str) -> int:
        """Return the address associated with the symbol.

        Args:
            symbol (str): The symbol to query.

        Returns:
            int: The address associated with the symbol.
        """
        return self.symbol_table[symbol]

    def get_available_slot(self) -> int:
        """Return the next available slot in the symbol table.

        Returns:
            int: The next available memory slot
        """
        slot = self._next_available_entry
        self._next_available_entry += 1
        return slot
