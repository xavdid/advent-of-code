# prompt: https://adventofcode.com/2018/day/1

from ...base import BaseSolution, InputTypes
from itertools import cycle


class Solution(BaseSolution):
    year = 2018
    input_type = InputTypes.INTARRAY

    def part_1(self):
        return sum(self.input)

    def part_2(self):
        s = set()
        c = 0
        for i in cycle(self.input):
            c += i
            if c in s:
                return c
            else:
                s.add(c)

