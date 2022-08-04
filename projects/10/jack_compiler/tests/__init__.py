"""Package containing testing routine."""


from typing import Literal

TestNames = Literal["array_test", "expression_less_square", "square"]
TestFiles = Literal[
    "in_path", "expected_token_path", "out_token_path", "expected_path", "out_path"
]
