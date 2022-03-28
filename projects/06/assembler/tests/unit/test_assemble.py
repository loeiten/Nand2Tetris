"""Module unit testing the assembler."""


from assembler.assemble import convert_to_15_bit_binary


def test_convert_to_15_bit_binary() -> None:
    """Test the functionality of convert_to_15_bit_binary."""
    assert convert_to_15_bit_binary("0") == "000000000000000"
    assert convert_to_15_bit_binary(0) == "000000000000000"
    assert convert_to_15_bit_binary("1") == "000000000000001"
    assert convert_to_15_bit_binary(1) == "000000000000001"
    assert convert_to_15_bit_binary("2") == "000000000000010"
    assert convert_to_15_bit_binary(2) == "000000000000010"
    assert convert_to_15_bit_binary("3") == "000000000000011"
    assert convert_to_15_bit_binary(3) == "000000000000011"
    assert convert_to_15_bit_binary("32767") == "111111111111111"
    assert convert_to_15_bit_binary(32767) == "111111111111111"
    assert convert_to_15_bit_binary(21845) == "101010101010101"
    assert convert_to_15_bit_binary("21845") == "101010101010101"
