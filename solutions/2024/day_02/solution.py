# prompt: https://adventofcode.com/2024/day/2

from itertools import pairwise
from typing import Iterable

from ...base import StrSplitSolution, answer
from ...utils.transformations import parse_ints


def is_strictly_increasing(vals: list[int]) -> bool:
    return all(l < r and 1 <= r - l <= 3 for l, r in pairwise(vals))


def is_safe(vals: list[int]) -> bool:
    return is_strictly_increasing(vals) or is_strictly_increasing(vals[::-1])


def omit_one(vals: list[int]) -> Iterable[list[int]]:
    for idx in range(len(vals)):
        yield vals[:idx] + vals[idx + 1 :]


class Solution(StrSplitSolution):
    _year = 2024
    _day = 2

    @answer(432)
    def part_1(self) -> int:
        return sum(is_safe(parse_ints(line.split())) for line in self.input)

    @answer(488)
    def part_2(self) -> int:
        lists = [parse_ints(line.split()) for line in self.input]

        return sum(is_safe(l) or any(is_safe(o) for o in omit_one(l)) for l in lists)
