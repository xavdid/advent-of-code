# prompt: https://adventofcode.com/2021/day/7

from functools import cache
from ...base import IntSplitSolution, answer


@cache
def range_sum(i: int) -> int:
    return i * (i + 1) // 2


class Solution(IntSplitSolution):
    _year = 2021
    _day = 7
    separator = ","

    @answer(340056)
    def part_1(self) -> int:
        min_result = sum(self.input)  # distance to 0
        for i in range(1, max(self.input)):
            distance_to_i = sum([abs(i - x) for x in self.input])
            min_result = min(min_result, distance_to_i)

        return min_result

    @answer(96592275)
    def part_2(self) -> int:
        min_result = 100_000_000
        for i in range(1, max(self.input)):
            distance_to_i = sum([range_sum(abs(i - x)) for x in self.input])
            min_result = min(min_result, distance_to_i)

        return min_result
