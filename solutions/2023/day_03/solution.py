# prompt: https://adventofcode.com/2023/day/3

import re
from collections import defaultdict
from operator import mul
from typing import TYPE_CHECKING

from ...base import StrSplitSolution, answer

if TYPE_CHECKING:
    from solutions.utils.graphs import GridPoint


class Solution(StrSplitSolution):
    _year = 2023
    _day = 3

    def pad_input(self) -> list[str]:
        width = len(self.input[0])
        # ensure every line is the same length; we'll mess up lines if it's not
        assert all(len(l) == width for l in self.input)

        return [
            "." * (width + 2),
            *[f".{l}." for l in self.input],
            "." * (width + 2),
        ]

    @answer(550934)
    def part_1(self) -> int:
        total = 0
        symbols = re.compile(r"[^\w.]")
        grid = self.pad_input()

        for line_num, line in enumerate(grid):
            for number in re.finditer(r"\d+", line):
                checks = [
                    # A - previous line
                    symbols.search(
                        grid[line_num - 1][number.start() - 1 : number.end() + 1],
                    ),
                    # B
                    symbols.search(line[number.start() - 1]),
                    # C
                    symbols.search(line[number.end()]),
                    # D
                    symbols.search(
                        grid[line_num + 1][number.start() - 1 : number.end() + 1],
                    ),
                ]

                if any(checks):
                    total += int(number.group())

        return total

    @answer(81997870)
    def part_2(self) -> int:
        gears: dict[GridPoint, list[int]] = defaultdict(list)

        grid = self.pad_input()

        for line_num, line in enumerate(grid):
            for number in re.finditer(r"\d+", line):
                # A
                if "*" in (
                    l := grid[line_num - 1][number.start() - 1 : number.end() + 1]
                ):
                    assert l.count("*") == 1
                    gears[(line_num - 1, number.start() - 1 + l.index("*"))].append(
                        int(number.group())
                    )

                # B
                if line[number.start() - 1] == "*":
                    gears[(line_num, number.start() - 1)].append(int(number.group()))

                # C
                if line[number.end()] == "*":
                    gears[(line_num, number.end())].append(int(number.group()))

                # D
                if "*" in (
                    l := grid[line_num + 1][number.start() - 1 : number.end() + 1]
                ):
                    assert l.count("*") == 1
                    gears[(line_num + 1, number.start() - 1 + l.index("*"))].append(
                        int(number.group())
                    )

        return sum([mul(*nums) for nums in gears.values() if len(nums) == 2])
