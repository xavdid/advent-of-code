# prompt: https://adventofcode.com/2019/day/16

from itertools import cycle
from typing import Iterator, List

from ...base import BaseSolution

BASE_PATTERN = [0, 1, 0, -1]


def flatten(unflat_list: List[List[int]]):
    return [item for sublist in unflat_list for item in sublist]


def pattern_for_step(loop: int) -> Iterator[int]:
    res = cycle(flatten([list([i] * (loop + 1)) for i in BASE_PATTERN]))
    # always skip the first item
    next(res)
    return res


def digit_place(i: int):
    return int(str(i)[-1])


class Solution(BaseSolution):
    year = 2019
    number = 16

    def part_1(self):
        num_loops = 100
        result = self.input
        self.pp(result)

        for loop in range(1, num_loops + 1):
            next_result = []
            for index in range(len(result)):
                pattern = pattern_for_step(index)
                next_result.append(
                    digit_place(sum([int(digit) * next(pattern) for digit in result]))
                )
            result = next_result
            self.pp(f"after {loop} phase: {result}")

        return "".join([str(i) for i in result][:8])

    def part_2(self):
        pass

    def solve(self):
        pass
