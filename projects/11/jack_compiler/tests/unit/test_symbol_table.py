"""Module containing test for the SymbolTable."""

from jack_compiler.symbol_table import SymbolTable


def test___init__() -> None:
    """Test the constructor."""
    class_table = SymbolTable()
    subroutine_table = SymbolTable()

    assert len(class_table.table) == 0
    assert len(subroutine_table.table) == 0
    assert class_table != subroutine_table


def test_define() -> None:
    """Test the define function."""
    table = SymbolTable()
    table.define("foo", "MyClass", "STATIC")
    table.define("bar", "MyClass", "FIELD")
    table.define("baz", "int", "STATIC")

    assert table.table == {
        "foo": {"type": "MyClass", "kind": "static", "index": 0},
        "bar": {"type": "MyClass", "kind": "field", "index": 0},
        "baz": {"type": "int", "kind": "static", "index": 1},
    }

    assert table.kind_indices["static"] == 1
    assert table.kind_indices["field"] == 0


def test_var_count() -> None:
    """Test the variable count."""
    table = SymbolTable()
    table.define("foo", "MyClass", "STATIC")
    table.define("bar", "MyClass", "FIELD")
    table.define("baz", "int", "STATIC")
    table.define("fooBar", "int", "ARG")
    table.define("qux", "char", "ARG")

    assert table.var_count("STATIC") == 2
    assert table.var_count("FIELD") == 1
    assert table.var_count("ARG") == 2
    assert table.var_count("VAR") == 0


def test_kind_of() -> None:
    """Test the kind of function."""
    table = SymbolTable()
    table.define("foo", "MyClass", "STATIC")
    table.define("bar", "MyClass", "FIELD")
    table.define("baz", "int", "ARG")
    table.define("fooBar", "int", "VAR")

    assert table.kind_of("foo") == "STATIC"
    assert table.kind_of("bar") == "FIELD"
    assert table.kind_of("baz") == "ARG"
    assert table.kind_of("fooBar") == "VAR"
    assert table.kind_of("qux") is None


def test_type_of() -> None:
    """Test the type of function."""
    table = SymbolTable()
    table.define("foo", "MyClass", "STATIC")
    table.define("bar", "int", "VAR")

    assert table.type_of("foo") == "MyClass"
    assert table.type_of("bar") == "int"


def test_index_of() -> None:
    """Test the index of function."""
    class_table = SymbolTable()
    class_table.define("foo", "MyClass", "STATIC")
    class_table.define("bar", "MyClass", "FIELD")
    class_table.define("baz", "int", "STATIC")

    assert class_table.index_of("foo") == 0
    assert class_table.index_of("bar") == 0
    assert class_table.index_of("baz") == 1

    subroutine_table = SymbolTable()
    subroutine_table.define("bar", "MyClass", "ARG")
    subroutine_table.define("baz", "int", "VAR")
    subroutine_table.define("foo", "MyClass", "VAR")

    assert class_table.index_of("bar") == 0
    assert class_table.index_of("foo") == 0
    assert class_table.index_of("baz") == 1

    assert subroutine_table.index_of("bar") == 0
    assert subroutine_table.index_of("baz") == 0
    assert subroutine_table.index_of("foo") == 1
