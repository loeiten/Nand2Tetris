"""Module unit testing the SymbolTable."""

from assembler.symbol_table import SymbolTable


def test_add_entry() -> None:
    """Test the functionality of SymbolTable.add_entry."""
    symbol_table = SymbolTable()
    assert "FOO" not in symbol_table.symbol_table.keys()
    assert "bar" not in symbol_table.symbol_table.keys()
    symbol_table.add_entry("FOO", 123)
    assert symbol_table.symbol_table["FOO"] == 123
    symbol_table.add_entry("bar", 99)
    assert symbol_table.symbol_table["bar"] == 99


def test_contains() -> None:
    """Test the functionality of SymbolTable.contains."""
    symbol_table = SymbolTable()
    assert symbol_table.contains("R0")
    assert not symbol_table.contains("bar")
    symbol_table.add_entry("bar", 99)
    assert symbol_table.contains("bar")


def test_get_address() -> None:
    """Test the functionality of SymbolTable.get_address."""
    symbol_table = SymbolTable()
    assert symbol_table.get_address("R0") == 0
    symbol_table.add_entry("bar", 99)
    assert symbol_table.get_address("bar") == 99


def test_get_available_slot() -> None:
    """Test the functionality of SymbolTable.get_available_slot."""
    symbol_table = SymbolTable()
    assert symbol_table.get_available_slot() == 16
    assert symbol_table.get_available_slot() == 17
