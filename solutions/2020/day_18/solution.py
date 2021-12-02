# prompt: https://adventofcode.com/2020/day/18

import ast
from operator import __add__, __mul__
from typing import Tuple

from ...base import BaseSolution, InputTypes

# part 1

OPERATORS = {"+": __add__, "*": __mul__}


def solve(equation: str) -> Tuple[int, int]:
    number = None
    operator = None
    pointer = 0

    while pointer < len(equation):
        head = equation[pointer]
        if head in OPERATORS:
            operator = OPERATORS[head]
        else:
            if head == ")":
                return number, pointer

            if head == "(":
                head, offset = solve(equation[pointer + 1 :])
                # extra 1 because the sub-function offset started at 0
                pointer += offset + 1

            if operator:
                # pylint: disable=not-callable
                number = operator(int(head), number)
                operator = None
            else:
                number = int(head)

        pointer += 1

    # pointer doesn't matter for final return
    return number, 0


# part 2


class SwapPrecedence(ast.NodeTransformer):
    # pylint: disable=no-self-use,unused-argument
    def visit_Sub(self, node):
        return ast.Mult()

    def visit_Div(self, node):
        return ast.Add()


class Solution(BaseSolution):
    _year = 2020
    _day = 18
    input_type = InputTypes.STRSPLIT

    def part_1(self) -> int:
        return sum([solve(line.replace(" ", ""))[0] for line in self.input])

    def part_2(self) -> int:
        total = 0
        for line in self.input:
            tree = ast.parse(line.replace("+", "/").replace("*", "-"), mode="eval")
            new_tree = SwapPrecedence().visit(tree)
            # pylint: disable=eval-used
            total += eval(compile(new_tree, filename="", mode="eval"))

        return total
