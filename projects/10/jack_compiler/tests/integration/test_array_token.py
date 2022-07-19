"""Test ArrayTest."""

from pathlib import Path

from jack_compiler.jack_analyzer import process_file


def test_array_test(tmp_path: Path, data_path: Path) -> None:
    """Test that the output of the jack compiler matches that of ArrayTest.

    Args:
        tmp_path (Path): Path to temporary directory
        data_path (Path): Path to the data path
    """
    in_path = data_path.joinpath("ArrayTest", "")
    out_path = in_path.with_suffix(".xml")
    print(f"FIXME: {out_path}, {tmp_path}, {process_file}")
