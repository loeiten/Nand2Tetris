"""Module containing the SymbolTable class."""

from typing import Dict, Literal, Optional, TypedDict

KIND = Literal["STATIC", "FIELD", "ARG", "VAR"]


class SymbolTable:
    """Class to populate the compiler's symbol table."""

    def __init__(self) -> None:
        """Create a new symbol table."""
        # NOTE: The total = True (default) guarantees that all keys must be present
        table_entry_type = TypedDict(
            "table_entry_type", {"type": str, "kind": KIND, "index": int}, total=True
        )
        self.table: Dict[str, table_entry_type] = dict()
        self.kind_indices: Dict[str, int] = dict()

    def define(self, name: str, identifier_type: str, kind: KIND) -> None:
        """Define a new identifier, and assigns it a running index.

        STATIC and FIELD identifiers have a class scope, while ARG and VAR
        identifiers have a subroutine scope.

        Args:
            name (str): Name of the identifier
            identifier_type (str): Type of the identifier
            kind (KIND): Kind of the identifier
        """
        # Update the index
        if identifier_type in self.kind_indices.keys():
            self.kind_indices[identifier_type] += 1
        else:
            self.kind_indices[identifier_type] = 1

        self.table[name] = {
            "type": identifier_type,
            "kind": kind,
            "index": self.kind_indices[identifier_type],
        }

    def var_count(self, kind: KIND) -> int:
        """Return the number of variables already defined in the current scope.

        Args:
            kind (KIND): The kind to find the current variables for

        Returns:
            int: The number of variables
        """
        return self.kind_indices[kind]

    def kind_of(self, name: str) -> Optional[KIND]:
        """Return the kind of the named identifier in the current scope.

        Args:
            name (str): Name of the identifier

        Returns:
            Optional[KIND]: The kind of the named identifier.
                If the identifier is unknown in the current scope, return None
        """
        return self.table[name]["kind"]

    def type_of(self, name: str) -> str:
        """Return the type of the named identifier in the current scope.

        Args:
            name (str): Name of the identifier

        Returns:
            str: The type of the identifier
        """
        return self.table[name]["type"]

    def index_of(self, name: str) -> int:
        """Return the type of the index assigned to the named identifier.

        Args:
            name (str): Name of the identifier

        Returns:
            int: The corresponding index
        """
        return self.table[name]["index"]
