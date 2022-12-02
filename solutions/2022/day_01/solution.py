# prompt: https://adventofcode.com/2022/day/1

from typing import Tuple

from ...base import TextSolution, answer


class Solution(TextSolution):
    _year = 2022
    _day = 1

    @answer((68292, 203203))
    def solve(self) -> Tuple[int, int]:
        raw_elves = self.input.split("\n\n")
        elves = sorted(sum(map(int, elf.split("\n"))) for elf in raw_elves)
        return elves[-1], sum(elves[-3:])
