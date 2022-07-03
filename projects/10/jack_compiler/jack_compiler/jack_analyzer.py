#!/usr/bin/env python

"""File containing functions for translating .jack files to .xlm files."""

import argparse
from pathlib import Path

from jack_compiler.compilation_engine import CompilationEngine
from jack_compiler.jack_tokenizer import JackTokenizer


def parse_args() -> argparse.Namespace:
    """Parse input arguments.

    Returns:
        argparse.Namespace: The parsed arguments
    """
    parser = argparse.ArgumentParser(
        description="Compile Jack code to Hack Virtual Machine code"
    )
    parser.add_argument(
        "path",
        type=Path,
        help="Directory or file containing Jack code to translate to Hack Virtual Machine code",
    )
    return parser.parse_args()


def process_file(in_path: Path) -> None:
    """Process a single file.

    Args:
        file_to_parse (Path): File to parse
    """
    print(f"Processing {in_path}...", end="\r")
    out_path = in_path.with_suffix(".xml")

    with in_path.open("r", encoding="utf-8") as in_file, out_path.open(
        "w", encoding="utf-8"
    ) as out_file:
        jack_tokenizer = JackTokenizer(in_file)
        compilation_engine = CompilationEngine(in_file=in_file, out_file=out_file)

        print(out_file)
        print(compilation_engine)

        while jack_tokenizer.has_more_tokens():
            jack_tokenizer.advance()

    print(f"Processing {in_path}...{out_path} written")


def main(in_path: Path) -> None:
    """Translate Jack code to Hack Virtual Machine code.

    The input xxx.jack will be translated to xxx.vm.

    Args:
        in_path (Path): File or directory to translate

    Raises:
        ValueError: If a input directory contains no .jack file
        ValueError: If the input file is not a .jack file
    """
    if in_path.is_dir():
        files_to_parse = list(in_path.glob("*.jack"))
        if len(files_to_parse) == 0:
            raise ValueError(f"{in_path} contains no *.jack files")
    else:
        if in_path.suffix != ".jack":
            raise ValueError(f"{in_path} is not a .jack file")
        files_to_parse = [in_path]

    for file_to_parse in files_to_parse:
        process_file(file_to_parse)


if __name__ == "__main__":
    args = parse_args()
    main(args.path.resolve())
