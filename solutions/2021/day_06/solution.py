# prompt: https://adventofcode.com/2021/day/6

from collections import defaultdict
from typing import Tuple

from ...base import IntSplitSolution, answer


class Solution(IntSplitSolution):
    _year = 2021
    _day = 6
    separator = ","

    @answer((350605, 1592778185024))
    def solve(self) -> Tuple[int, int]:
        part_1 = 0

        result = defaultdict(int)

        for i in self.input:
            result[i] += 1

        for day in range(256):
            if day == 80:
                part_1 = sum(result.values())

            new_result = defaultdict(int)
            for fish, num in result.items():
                if fish == 0:
                    new_result[6] += num
                    new_result[8] += num
                else:
                    new_result[fish - 1] += num
            result = new_result

        return part_1, sum(result.values())
