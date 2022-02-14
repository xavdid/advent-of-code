# prompt: https://adventofcode.com/2021/day/24


from functools import partial
from typing import Iterable, List, Literal, Optional, Union
from ...base import StrSplitSolution, answer

from dataclasses import dataclass


def chunks(lst: List[str], n: int) -> Iterable[List[str]]:
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i : i + n]


def get_val(line: str) -> int:
    return int(line.split()[-1])


@dataclass
class Item:
    # which place in the final number
    digit: int
    # push or pop
    operation: int
    # the value we'll contribute to the equation
    value: int

    @property
    def is_push(self) -> bool:
        return self.operation == 1


class Solution(StrSplitSolution):
    _year = 2021
    _day = 24

    # @answer(1234)
    def part_1(self) -> int:
        def sub_prog(a, b, c, i, z):
            w, x, y = 0, 0, 0

            w = i  # INPUT
            x *= 0  # RESET X
            x += z  # X = Z (ans from previous section)
            x %= 26  # X shift to letter?
            z //= a  # VAR; 1 or 26 forms a pair where 26 is used instead
            x += b  # VAR; OFFSET
            x = int(x == w)  # X == W?
            x = int(x == 0)  # X = !X; true if X != W
            y *= 0  # RESET Y
            y += 25  # Y = 25
            y *= x  # if X was equal to W, then Y is 0; otherwise 25
            y += 1  # Y is 1 or 26
            z *= y  #
            y *= 0  # RESET Y
            y += w  # Y = W
            y += c  # VAR
            y *= x
            z += y

            return z

        stack: List[Item] = []
        result: List[str] = [""] * 14

        for idx, block in enumerate(chunks(self.input, 18)):
            assert idx <= 13
            op = get_val(block[4])

            val = get_val(block[15 if op == 1 else 5])

            i = Item(idx, op, val)

            if i.is_push:
                stack.append(i)
                continue

            # the higher-power number
            prev = stack.pop()

            # the pair of numbers must differ by this much
            diff = prev.value + i.value
            assert diff <= 8
            # print(diff)
            # go high or low?
            if False:
                if diff > 0:
                    result[prev.digit] = str(9 - diff)
                    result[i.digit] = str(9)
                else:
                    result[prev.digit] = str(9)
                    result[i.digit] = str(9 + diff)
            else:
                if diff > 0:
                    result[prev.digit] = str(1)
                    result[i.digit] = str(1 + diff)
                else:
                    result[prev.digit] = str(1 - diff)
                    result[i.digit] = str(1)

        assert all(result)
        assert len(result) == 14
        # print(result)
        out = "".join(result)
        assert len(out) == 14
        return int(out)

    # @answer(1234)
    def part_2(self) -> int:
        pass

    # @answer((1234, 4567))
    # def solve(self) -> Tuple[int, int]:
    #     pass
