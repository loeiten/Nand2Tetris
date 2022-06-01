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
        "path",
        type=Path,
        help="Directory or file containing Hack Virtual Machine code to translate to symbolic "
        "Hack assembly code",
    )
    return parser.parse_args()


def process_file(file_to_parse: Path, code_writer: CodeWriter) -> None:
    """Process a single file.

    Args:
        file_to_parse (Path): File to parse
        code_writer (CodeWriter): The code writer to ues
    """
    print(f"Processing {file_to_parse}...")
    parser = Parser(str(file_to_parse))
    code_writer.set_file_name(file_to_parse.name)

    while parser.has_more_commands():
        parser.advance()
        command_type = parser.command_type()
        if command_type != "C_RETURN":
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
        elif command_type == "C_LABEL":
            code_writer.write_label(label=arg1)
        elif command_type == "C_GOTO":
            code_writer.write_goto(label=arg1)
        elif command_type == "C_IF":
            code_writer.write_if(label=arg1)
        elif command_type == "C_FUNCTION":
            num_vars = parser.arg2()
            code_writer.write_function(function_name=arg1, num_vars=num_vars)
        elif command_type == "C_CALL":
            num_args = parser.arg2()
            code_writer.write_call(function_name=arg1, num_args=num_args)
        elif command_type == "C_RETURN":
            code_writer.write_return()


def main(in_path: Path) -> None:
    """Translate a Hack Virtual Machine code to symbolic Hack assembly code.

    The input xxx.vm will be translated to xxx.asm.

    Args:
        in_path (Path): File or directory to translate

    Raises:
        ValueError: If a input directory contains no .vm file
        ValueError: If the input file is not a .vm file
    """
    if in_path.is_dir():
        files_to_parse = list(in_path.glob("*.vm"))
        if len(files_to_parse) == 0:
            raise ValueError(f"{in_path} contains no *.vm files")
        print(f"{in_path} is a dir, will write bootstrap code")
    else:
        if in_path.suffix != ".vm":
            raise ValueError(f"{in_path} is not a .vm file")
        files_to_parse = [in_path]
        print(f"{in_path} is a file, will write NOT bootstrap code")

    in_dir = files_to_parse[0].parent
    code_writer = CodeWriter(
        str(in_dir.joinpath(in_dir.name).with_suffix(".asm")),
        bootstrap=in_path.is_dir(),
    )

    for file_to_parse in files_to_parse:
        process_file(file_to_parse, code_writer)

    print(f"{code_writer.out_path} written!")


if __name__ == "__main__":
    args = parse_args()
    main(args.path.resolve())
