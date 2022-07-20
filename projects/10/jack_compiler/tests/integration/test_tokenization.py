"""Test tokenization."""

from pathlib import Path

from jack_compiler.jack_analyzer import process_file


def test_array_test(tmp_path: Path, array_test_path: Path) -> None:
    """Test that the output of the jack compiler matches that of ArrayTest.

    Args:
        tmp_path (Path): Path to temporary directory
        data_path (Path): Path to the ArrayTest directory
    """
    in_path = array_test_path.joinpath("Main.jack")
    expected_path = array_test_path.joinpath("MainT.xml")

    out_path = tmp_path.joinpath("MainT.xml")

    process_file(in_path=in_path, tokens_only=True, out_path=out_path)
    with out_path.open("r+") as out_file:
        lines = out_file.readlines()
        lines.insert(0, "<tokens>\n")
        lines.append("</tokens>\n")
        out_file.seek(0)
        out_file.writelines(lines)

    with expected_path.open("r", encoding="utf-8") as expected_file:
        expected_lines = expected_file.readlines()

    with out_path.open("r", encoding="utf-8") as out_file:
        out_lines = out_file.readlines()

    assert expected_lines == out_lines
