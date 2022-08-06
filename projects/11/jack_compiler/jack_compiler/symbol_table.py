"""Module containing the SymbolTable class."""

from typing import Literal, Optional

KIND = Literal["STATIC", "FIELD", "ARG", "VAR"]


class SymbolTable:
    """Class to populate the compiler's symbol table."""

    def __init__(self) -> None:
        """Create a new symbol table."""

    def define(self, name: str, identifier_type: str, kind: KIND) -> None:
        """Define a new identifier, and assigns it a running index.

        STATIC and FIELD identifiers have a class scope, while ART and VAR
        identifiers have a subroutine scope.

        Args:
            name (str): Name of the identifier
            identifier_type (str): Type of the identifier
            kind (KIND): Kind of the identifier
        """

    def var_count(self, kind: KIND) -> int:
        """Return the number of variables already defined in the current scope.

        Args:
            kind (KIND): The kind to find the current variables for

        Returns:
            int: The number of variables
        """

    def kind_of(self, name: str) -> Optional[KIND]:
        """Return the kind of the named identifier in the current scope.

        Args:
            name (str): Name of the identifier

        Returns:
            Optional[KIND]: The kind of the named identifier.
                If the identifier is unknown in the current scope, return None
        """

    def type_of(self, name: str) -> str:
        """Return the type of the named identifier in the current scope.

        Args:
            name (str): Name of the identifier

        Returns:
            str: The type of the identifier
        """

    def index_of(self, name: str) -> int:
        """Return the type of the index assigned to the named identifier.

        Args:
            name (str): Name of the identifier

        Returns:
            int: The corresponding index
        """
