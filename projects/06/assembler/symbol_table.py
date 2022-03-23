class SymbolTable:
    def __init__(self) -> None:
        """Create a new empty symbol table."""
        pass

    def add_entry(self, symbol: str, address: int) -> None:
        """Add <symbol, address> to the table.

        Args:
            symbol (str): The symbol to add to the table.
            address (int): The corresponding address.
        """
        pass

    def contains(self, symbol: str) -> bool:
        """Check if the symbol table contains the symbol.

        Args:
            symbol (str): The symbol to query.

        Returns:
            bool: True if the symbol is contained.
        """
        pass

    def get_address(self, symbol: str) -> int:
        """Return the address associated with the symbol.

        Args:
            symbol (str): The symbol to query.

        Returns:
            int: The address associated with the symbol.
        """
        pass