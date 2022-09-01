#!/usr/bin/env python

"""File containing functions for translating .asm files to .hack files."""

import argparse
from pathlib import Path
from typing import Union

from assembler.code import Code
from assembler.parser import Parser
from assembler.symbol_table import SymbolTable

MAX_INT = (2**15) - 1


def parse_args() -> argparse.Namespace:
    """Parse input arguments.

    Returns:
        argparse.Namespace: The parsed arguments
    """
    parser = argparse.ArgumentParser(
        description="Translate a symbolic Hack program into Hack instructions"
    )
    parser.add_argument(
        "file",
        type=Path,
        help="Symbolic Hack program to translate into Hack instructions",
    )
    return parser.parse_args()


def main(in_path: Path) -> None:
    """Translate symbolic Hack machine language into binary hack instructions.

    The input xxx.asm will be translated to xxxNoSymbol.asm and xxx.hack where
    - xxxL.asm is the stripped symbolic instruction where:
        - Comments and whitespace has been stripped
        - Symbols have been translated to decimals
        - Labels have been removed
    - xxx.hack is the binary instructions for the Hack program

    Args:
        in_path (Path): File to translate
    """
    symbol_table = first_pass(in_path)
    second_pass(in_path=in_path, symbol_table=symbol_table)


def first_pass(in_path: Path) -> SymbolTable:
    """Fill the symbol table.

    Args:
        in_path (Path): File used to generate the symbol table

    Returns:
        SymbolTable: The filled symbol table
    """
    parser = Parser(str(in_path))
    symbol_table = SymbolTable()
    instruction_line = 0

    a_instruction_symbols = list()
    while parser.has_more_lines():
        parser.advance()
        if parser.instruction_type() == "L_INSTRUCTION":
            # NOTE: An L_INSTRUCTION does not count as an instruction,
            #        but is referring to the next instruction line
            # In an error-free code there will only be one definition of an L-instruction
            symbol_table.add_entry(symbol=parser.symbol(), address=instruction_line)
        else:
            if parser.instruction_type() == "A_INSTRUCTION":
                cur_symbol = parser.symbol()
                if (
                    not cur_symbol.isdigit()
                    and not symbol_table.contains(cur_symbol)
                    and cur_symbol not in a_instruction_symbols
                ):
                    a_instruction_symbols.append(cur_symbol)

            # Update the instruction line for A and C instructions
            instruction_line += 1

    # pylint: disable=consider-iterating-dictionary
    for cur_symbol in symbol_table.symbol_table.keys():
        if cur_symbol in a_instruction_symbols:
            a_instruction_symbols.remove(cur_symbol)

    for cur_symbol in a_instruction_symbols:
        symbol_table.add_entry(
            symbol=cur_symbol, address=symbol_table.get_available_slot()
        )

    return symbol_table


def second_pass(in_path: Path, symbol_table: SymbolTable) -> None:
    """Write the xxxNoSymbol.asm and xxx.hack file.

    Args:
        in_path (Path): File to translate from
        symbol_table (SymbolTable): Symbol table to use
    """
    # The l-path will contain the stripped file without symbols
    no_symbol_path = in_path.parent.joinpath(f"{in_path.stem}NoSymbol{in_path.suffix}")
    hack_path = in_path.with_suffix(".hack")

    parser = Parser(str(in_path))
    code = Code()

    with no_symbol_path.open("w") as l_file, hack_path.open(
        "w", encoding="ASCII"
    ) as hack_file:
        while parser.has_more_lines():
            parser.advance()
            # NOTE: L-instructions are not translated
            if parser.instruction_type() == "L_INSTRUCTION":
                continue
            if parser.instruction_type() == "A_INSTRUCTION":
                cur_symbol = parser.symbol()
                if not cur_symbol.isdigit():
                    symbol_instruction = f"@{symbol_table.get_address(cur_symbol)}"
                else:
                    symbol_instruction = f"@{cur_symbol}"
                binary_instruction = convert_to_15_bit_binary(
                    symbol_instruction.strip("@")
                )
                # Add the leading 0 which marks that this is an A-instruction
                binary_instruction = f"0{binary_instruction}"
            if parser.instruction_type() == "C_INSTRUCTION":
                if isinstance(parser.current_instruction, str):
                    symbol_instruction = parser.current_instruction
                    comp = code.comp(parser.comp())
                    dest = code.dest(parser.dest())
                    jump = code.jump(parser.jump())
                    # Add the three leading 1 which marks that this is a C-instruction
                    binary_instruction = f"111{comp}{dest}{jump}"
                else:
                    binary_instruction = (
                        "Error: parser.current_instruction was not string"
                    )

            l_file.write(f"{symbol_instruction.replace(' ', '')}\n")
            hack_file.write(f"{binary_instruction}\n")


def convert_to_15_bit_binary(decimal: Union[str, int]) -> str:
    """Convert a decimal string into a 15 bit binary string.

    Args:
        decimal (Union[str, int]): The decimal to convert.

    Raises:
        RuntimeError: If the decimal is too large

    Returns:
        str: The corresponding binary string.
    """
    decimal = int(decimal)
    if decimal > MAX_INT:
        raise RuntimeError(
            f"{decimal} > {MAX_INT}. Cannot make 15 bit binary representation."
        )
    binary_string = ""
    # NOTE: range(i) represents the numbers [0, 15)
    for exponent in range(15)[::-1]:
        divisor = 2**exponent
        binary_string += str(decimal // divisor)
        decimal = decimal % divisor

    return binary_string


if __name__ == "__main__":
    args = parse_args()
    main(args.file.resolve())
