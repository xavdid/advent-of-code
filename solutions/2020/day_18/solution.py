# prompt: https://adventofcode.com/2020/day/18

from operator import __add__, __mul__
from typing import List, Tuple

from ...base import BaseSolution, InputTypes

# from typing import Tuple

OPERATORS = {"+": __add__, "*": __mul__}


def solve(equation: str) -> Tuple[int, int]:

    # print("\ncalling with", equation)

    number = None
    operator = None
    pointer = 0

    while pointer < len(equation):
        head = equation[pointer]
        # print(f'{pointer=} ("{head=}")')
        if head in OPERATORS:
            operator = OPERATORS[head]
        else:
            if head == ")":
                # print(f"returning {number[0]} {pointer=}", "\n")
                return number, pointer

            if head == "(":
                # strip off the first paren and recurse the rest
                head, offset = solve(equation[pointer + 1 :])
                # print(pointer, offset)
                pointer += offset + 1
                # print(f'now looking at "{equation[pointer]}"')

            if operator:
                # pylint: disable=not-callable
                number = operator(int(head), number)
                operator = None
            else:
                number = int(head)

            # if should_return and subequation:
            #     print("returning", number[0], "\n")
            #     return number.pop()
        pointer += 1
        # print(
        #     f"{number=} {pointer=} (next is \"{equation[pointer] if pointer < len(equation) else 'done'}\") {operator=}"
        # )

    # print("final return", number[0], "\n")
    # pointer doesn't matter for final return
    return number, 0


class Solution(BaseSolution):
    year = 2020
    number = 18
    input_type = InputTypes.STRSPLIT

    def part_1(self) -> int:
        return sum([solve(line.replace(" ", ""))[0] for line in self.input])

    def part_2(self) -> int:
        pass

    # def solve(self) -> Tuple[int, int]:
    #     pass
