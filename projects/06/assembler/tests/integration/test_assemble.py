"""Module integration testing the assembler."""

from pathlib import Path

import pytest
from assembler.assemble import first_pass, main


@pytest.fixture(scope="function", name="data_tmp_dir")
def fixture_data_tmp_dir(tmp_path: Path, mult_path: Path, fill_path: Path) -> Path:
    """Return the temporary directory to where Mult.asm has been copied.

    Args:
        tmp_path (Path): Path to temporary directory
        mult_path (Path): Path to Mult.asm
        fill_path (Path): Path to Fill.asm

    Returns:
        Path: Path to temporary directory
    """
    tmp_mult = tmp_path.joinpath(mult_path.name)
    tmp_mult.write_text(mult_path.read_text())
    tmp_fill = tmp_path.joinpath(fill_path.name)
    tmp_fill.write_text(fill_path.read_text())
    return tmp_path


def test_first_pass_mult(data_tmp_dir: Path) -> None:
    """Test that first_pass creates the expected symbol table for the mult file.

    Args:
        data_tmp_dir (Path): Path to temporary directory containing Mult.asm
    """
    symbol_table = first_pass(data_tmp_dir.joinpath("Mult.asm"))
    assert symbol_table.symbol_table["lhs"] == 16
    assert symbol_table.symbol_table["rhs"] == 17
    assert symbol_table.symbol_table["i"] == 18
    assert symbol_table.symbol_table["LOOP"] == 12
    assert symbol_table.symbol_table["END"] == 27


def test_first_pass_fill(data_tmp_dir: Path) -> None:
    """Test that first_pass creates the expected symbol table for the fill file.

    Args:
        data_tmp_dir (Path): Path to temporary directory containing Fill.asm
    """
    symbol_table = first_pass(data_tmp_dir.joinpath("Fill.asm"))
    assert symbol_table.symbol_table["keyPressed"] == 16
    assert symbol_table.symbol_table["screenVal"] == 17
    assert symbol_table.symbol_table["i"] == 18
    assert symbol_table.symbol_table["row"] == 19
    assert symbol_table.symbol_table["lastRow"] == 20
    assert symbol_table.symbol_table["CHECKIFPRESSED"] == 22
    assert symbol_table.symbol_table["SETSCREENVALUE"] == 34
    assert symbol_table.symbol_table["MAINLOOP"] == 12
    assert symbol_table.symbol_table["SETKEYPRESSED"] == 30
    assert symbol_table.symbol_table["RETURNCHECKIFPRESSED"] == 14
    assert symbol_table.symbol_table["ENDSETSCREENVALUELOOP"] == 57
    assert symbol_table.symbol_table["SETSCREENVALUELOOP"] == 36


@pytest.mark.parametrize("file_name", ("Mult", "Fill"))
def test_main(data_tmp_dir: Path, data_path: Path, file_name: str) -> None:
    """Test that main creates the expected NoSymbol.asm and .hack file.

    Args:
        data_tmp_dir (Path): Path to temporary directory containing Mult.asm
        data_path(Path): Path to the data directory
        file_name (str): Name of file to use for the tests
    """
    no_symbol_ground_truth_path = data_path.joinpath(f"{file_name}NoSymbol.asm")
    hack_ground_truth_path = data_path.joinpath(f"{file_name}.hack")

    file_path = data_tmp_dir.joinpath(f"{file_name}.asm")
    main(file_path)
    tmp_dir = file_path.parent
    stem = file_path.stem
    suffix = file_path.suffix
    no_symbol_path = tmp_dir.joinpath(f"{stem}NoSymbol{suffix}")
    hack_path = tmp_dir.joinpath(f"{stem}.hack")

    # Check that the files has bee created
    assert no_symbol_path.is_file()
    assert hack_path.is_file()

    # Check the content of the l file is correct
    with no_symbol_ground_truth_path.open("r") as expected_file, no_symbol_path.open(
        "r"
    ) as result_file:
        for expected_line, result_line in zip(
            expected_file.readlines(), result_file.readlines()
        ):
            assert result_line == expected_line

    # Check the content of the hack file is correct
    with hack_ground_truth_path.open("r") as expected_file, hack_path.open(
        "r"
    ) as result_file:
        for expected_line, result_line in zip(
            expected_file.readlines(), result_file.readlines()
        ):
            assert result_line == expected_line
