# prompt: https://adventofcode.com/2019/day/16

from itertools import cycle
from typing import Iterator

from ...base import BaseSolution, slow

BASE_PATTERN = [0, 1, 0, -1]


def pattern_for_step(loop: int) -> Iterator[int]:
    pattern = []
    for i in BASE_PATTERN:
        pattern += list([i] * (loop + 1))
    res = cycle(pattern)
    # always skip the first item
    next(res)
    return res


class Solution(BaseSolution):
    _year = 2019
    _day = 16

    @slow
    def part_1(self):
        num_loops = 100
        result = self.input
        self.pp(result)

        for loop in range(1, num_loops + 1):
            next_result = []
            for index in range(len(result)):
                pattern = pattern_for_step(index)
                total = 0
                for digit in result:
                    total += int(digit) * next(pattern)
                next_result.append(total % 10)
            result = next_result
            self.pp(f"after phase {loop}: {result}")

        return "".join([str(i) for i in result][:8])

    def part_2(self):
        # copied this: https://github.com/mebeim/aoc/blob/master/2019/README.md#day-16---flawed-frequency-transmission

        to_skip = int(self.input[:7])
        digits = list((self.input * 10000)[to_skip:])
        length = len(digits)

        for _ in range(100):
            total = 0
            for i in range(length - 1, -1, -1):
                total += int(digits[i])
                digits[i] = total % 10

        return "".join([str(i) for i in digits[:8]])
