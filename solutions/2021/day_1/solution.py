# prompt: https://adventofcode.com/2021/day/1

from typing import List
from ...base import IntSplitSolution, answer


def num_increases(nums: List[int]) -> int:
    total = 0

    for index, i in enumerate(nums):
        if index > 0 and i > nums[index - 1]:
            total += 1

    return total


class Solution(IntSplitSolution):
    _year = 2021
    _day = 1

    @answer(1711)
    def part_1(self) -> int:
        return num_increases(self.input)

    @answer(1743)
    def part_2(self) -> int:
        return num_increases(
            [sum(x) for x in zip(self.input, self.input[1:], self.input[2:])]
        )
