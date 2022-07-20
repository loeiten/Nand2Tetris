#!/usr/bin/env python

"""File containing functions for translating .jack files to .xlm files."""

import argparse
from pathlib import Path
from typing import Optional, cast, get_args

from jack_compiler.compilation_engine import CompilationEngine, TerminalElement
from jack_compiler.jack_tokenizer import JackTokenizer

TOKEN_MAP = {
    "KEYWORD": {"text": "keyword", "function_name": "keyword"},
    "SYMBOL": {"text": "symbol", "function_name": "symbol"},
    "IDENTIFIER": {"text": "identifier", "function_name": "identifier"},
    "INT_CONST": {"text": "integerConstant", "function_name": "int_val"},
    "STRING_CONST": {"text": "stringConstant", "function_name": "string_val"},
}


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


def process_file(
    in_path: Path, tokens_only: bool = False, out_path: Optional[Path] = None
) -> None:
    """Process a single file.

    Args:
        file_to_parse (Path): File to parse
        tokens_only (bool, optional): Whether or not to only parse tokens. Defaults to False.
        out_path (Optional[Path], optional): The out path. Defaults to None.
    """
    print(f"Processing {in_path}...", end="\r")
    if out_path is None:
        out_path = in_path.with_suffix(".xml")

    with in_path.open("r", encoding="utf-8") as in_file, out_path.open(
        "w", encoding="utf-8"
    ) as out_file:
        jack_tokenizer = JackTokenizer(in_file)
        compilation_engine = CompilationEngine(in_file=in_file, out_file=out_file)

        while jack_tokenizer.has_more_tokens():
            jack_tokenizer.advance()
            token_type = jack_tokenizer.token_type()
            func = getattr(jack_tokenizer, TOKEN_MAP[token_type]["function_name"])
            token = func()
            compilation_token_type = TOKEN_MAP[token_type]["text"]
            if token_type == "KEYWORD":
                token = token.lower()
            if compilation_token_type not in get_args(TerminalElement):
                raise RuntimeError(
                    f"{compilation_token_type} not in {get_args(TerminalElement)}"
                )
            cast(TerminalElement, compilation_token_type)
            # Type ignore as mypy doesn't detect that we are ensuring the
            # correct input type for token_type
            compilation_engine.write_token(
                token_type=compilation_token_type, token=token  # type: ignore
            )
            if not tokens_only:
                # Process the grammar
                pass

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
