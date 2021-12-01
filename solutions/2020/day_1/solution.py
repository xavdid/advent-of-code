# prompt: https://adventofcode.com/2020/day/1

from itertools import combinations

from ...base import BaseSolution, InputTypes


class Solution(BaseSolution):
    _year = 2020
    _number = 1
    input_type = InputTypes.INTSPLIT

    def part_1(self) -> int:
        # for any item, we know what we're looking for.
        # So we can iterate each step, see if its pair exists, and if so, exit
        for amount in self.input:
            target = 2020 - amount
            if target in self.input:
                return amount * target

    def part_2(self) -> int:
        # need a list of pairs so we can search for the third
        for a, b in combinations(self.input, 2):
            target = 2020 - a - b
            if target in self.input:
                return a * b * target
