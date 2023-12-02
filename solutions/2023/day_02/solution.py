# prompt: https://adventofcode.com/2023/day/2

import re
from collections import defaultdict
from functools import reduce
from operator import mul

from ...base import StrSplitSolution, answer


class Solution(StrSplitSolution):
    _year = 2023
    _day = 2

    @answer(2716)
    def part_1(self) -> int:
        total = 0

        for idx, game_info in enumerate(self.input):
            _, marbles = game_info.split(": ")
            if all(
                int(count) <= {"red": 12, "green": 13, "blue": 14}[color]
                for count, color in re.findall(r"(\d+) (\w+)", marbles)
            ):
                total += idx + 1

        return total

    @answer(72227)
    def part_2(self) -> int:
        total = 0

        for game_info in self.input:
            _, marbles = game_info.split(": ")
            mins: dict[str, int] = defaultdict(int)

            for count, color in re.findall(r"(\d+) (\w+)", marbles):
                mins[color] = max(mins[color], int(count))

            total += reduce(mul, mins.values())

        return total
