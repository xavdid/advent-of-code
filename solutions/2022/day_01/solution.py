# prompt: https://adventofcode.com/2022/day/1

from typing import Tuple

from ...base import StrSplitSolution, answer


class Solution(StrSplitSolution):
    _year = 2022
    _day = 1

    separator = "\n\n"

    @answer((68292, 203203))
    def solve(self) -> Tuple[int, int]:
        elves = sorted(sum(map(int, elf.split("\n"))) for elf in self.input)
        return elves[-1], sum(elves[-3:])
