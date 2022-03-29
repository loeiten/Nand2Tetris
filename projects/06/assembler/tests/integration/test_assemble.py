"""Module integration testing the assembler."""

from pathlib import Path
from typing import Tuple

import pytest
from assembler.assemble import first_pass, main


@pytest.fixture(scope="function", name="mult_tmp_dir")
def fixture_mult_tmp_dir(tmp_path: Path, mult_path: Path) -> Path:
    """Return the temporary directory to where Mult.asm has been copied.

    Args:
        tmp_path (Path): Path to temporary directory
        mult_path (Path): Path to Mult.asm

    Returns:
        Path: Path to temporary directory
    """
    tmp_mult = tmp_path.joinpath(mult_path.name)
    tmp_mult.write_text(mult_path.read_text())
    return tmp_mult


@pytest.fixture(scope="session", name="no_symbol_and_hack")
def fixture_no_symbol_and_hack(mult_path: Path) -> Tuple[Path, ...]:
    """Return the path to the MultL.asm and Mult.hack files.

    Args:
        mult_path (Path): Path to Mult.asm

    Returns:
        Tuple[Path, ...]: Path to MultL.asm and Mult.hack
    """
    data_dir = mult_path.parent
    no_symbol_path = data_dir.joinpath("MultNoSymbol.asm")
    hack_path = data_dir.joinpath("Mult.hack")
    return no_symbol_path, hack_path


def test_first_pass(mult_tmp_dir: Path) -> None:
    """Test that first_pass creates the expected symbol table.

    Args:
        mult_timp_dir (Path): Path to temporary directory containing Mult.asm
    """
    symbol_table = first_pass(mult_tmp_dir)
    assert symbol_table.symbol_table["lhs"] == 16
    assert symbol_table.symbol_table["rhs"] == 17
    assert symbol_table.symbol_table["i"] == 18
    assert symbol_table.symbol_table["LOOP"] == 12
    assert symbol_table.symbol_table["END"] == 27


def test_main(mult_tmp_dir: Path, no_symbol_and_hack: Tuple[Path, ...]) -> None:
    """Test that main creates the expected L.asm and .hack file.

    Args:
        mult_timp_dir (Path): Path to temporary directory containing Mult.asm
        no_symbol_and_hack(Tuple[Path, ...]): Path to the ground truth MultL.asm and Mult.hack
    """
    no_symbol_ground_truth_path, hack_ground_truth_path = no_symbol_and_hack

    main(mult_tmp_dir)
    tmp_dir = mult_tmp_dir.parent
    stem = mult_tmp_dir.stem
    suffix = mult_tmp_dir.suffix
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
