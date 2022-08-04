"""Module unit testing the CodeWriter."""

from pathlib import Path
from typing import Literal

import pytest
from vm_translator.code_writer import CodeWriter


@pytest.fixture(scope="function", name="code_writer")
def fixture_code_writer(tmp_path: Path) -> CodeWriter:
    """Return the string path to the .asm file to write to.

    Args:
        tmp_path (Path): Path to temporary directory

    Returns:
        CodeWriter: The code writer object writing to tmp_path/test.asm
    """
    path = tmp_path.joinpath("test.asm")
    code_writer = CodeWriter(str(path))
    return code_writer


def test__init__(code_writer: CodeWriter) -> None:
    """Test that the CodeWriter constructor works as expected.

    Args:
        code_writer (CodeWriter): The code writer object
    """
    assert code_writer.file_name == "test"


@pytest.mark.parametrize(
    "command", ("add", "sub", "eq", "gt", "lt", "and", "or", "neg", "not")
)
def test_write_arithmetic(
    code_writer: CodeWriter,
    command: Literal["add", "sub", "eq", "gt", "lt", "and", "or", "neg", "not"],
) -> None:
    """Test that the write_arithmetic writes the command as expected.

    Note:
    The content is tested with the test files of the project

    Args:
        code_writer (CodeWriter): The code writer object
        command (Literal["add", "sub", "eq", "gt", "lt", "and", "or", "neg", "not"]):
            The command to translate into assembly
    """
    code_writer.write_arithmetic(command=command)
    file_path = Path(code_writer.file.name)
    code_writer.close()
    with file_path.open("r") as file:
        assert file.readline() == f"// {command}\n"


@pytest.mark.parametrize("command", ("C_PUSH", "C_POP"))
@pytest.mark.parametrize(
    "segment",
    ("local", "argument", "this", "that", "constant", "static", "pointer", "temp"),
)
def test_write_push_pop(
    code_writer: CodeWriter,
    command: Literal["C_PUSH", "C_POP"],
    segment: Literal[
        "local", "argument", "this", "that", "constant", "static", "pointer", "temp"
    ],
) -> None:
    """Test that the write_arithmetic writes the command as expected.

    Note:
    The content is tested with the test files of the project

    Args:
        code_writer (CodeWriter): The code writer object
        command (Literal["C_PUSH", "C_POP"]): The command to translate into assembly
        segment (Literal["local", "argument", "this", "that", "constant", "static", "pointer", "temp"]):
            Which virtual memory segment to push from/pop to
    """
    index = 1
    code_writer.write_push_pop(command=command, segment=segment, index=index)
    file_path = Path(code_writer.file.name)
    code_writer.close()
    command_map = {"C_PUSH": "push", "C_POP": "pop"}
    with file_path.open("r") as file:
        assert file.readline() == f"// {command_map[command]} {segment} {index}\n"
