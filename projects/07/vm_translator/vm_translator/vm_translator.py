#!/usr/bin/env python

"""File containing functions for translating .asm files to .hack files."""

import argparse
from pathlib import Path


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
    print(in_path)


if __name__ == "__main__":
    args = parse_args()
    main(args.file.resolve())
