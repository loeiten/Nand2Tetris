#!/usr/bin/env python

"""File containing functions for translating .asm files to .hack files."""

import argparse
from pathlib import Path

from vm_translator.code_writer import CodeWriter
from vm_translator.parser import Parser


def parse_args() -> argparse.Namespace:
    """Parse input arguments.

    Returns:
        argparse.Namespace: The parsed arguments
    """
    parser = argparse.ArgumentParser(
        description="Translate a Hack Virtual Machine code to symbolic Hack assembly code"
    )
    parser.add_argument(
        "file",
        type=Path,
        help="Hack Virtual Machine code to translate to symbolic Hack assembly code",
    )
    return parser.parse_args()


def main(in_path: Path) -> None:
    """Translate a Hack Virtual Machine code to symbolic Hack assembly code.

    The input xxx.vm will be translated to xxx.asm.

    Args:
        in_path (Path): File to translate
    """
    parser = Parser(str(in_path))
    code_writer = CodeWriter(str(in_path.with_suffix(".asm")))

    while parser.has_more_commands():
        parser.advance()
        command_type = parser.command_type()
        arg1 = parser.arg1()
        if command_type == "C_ARITHMETIC":
            # mypy correctly complains that segment want's a literal, and not a str
            # However, as we know that we are dealing with C_ARITHMETIC we know
            # that the argument can only be one of the literals
            code_writer.write_arithmetic(command=arg1)  # type: ignore
        # mypy throws error when using in
        # pylint: disable=consider-using-in
        elif command_type == "C_PUSH" or command_type == "C_POP":
            index = parser.arg2()
            # mypy correctly complains that segment want's a literal, and not a str
            # However, as we know that we are not dealing with C_ARITHMETIC we know
            # that the argument can only be one of the literals
            code_writer.write_push_pop(
                command=command_type, segment=arg1, index=index  # type: ignore
            )


if __name__ == "__main__":
    args = parse_args()
    main(args.file.resolve())
