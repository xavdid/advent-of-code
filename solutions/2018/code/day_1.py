# prompt: https://adventofcode.com/2018/day/1

from ...base import BaseSolution, InputTypes
from itertools import cycle


class Solution(BaseSolution):
    @property
    def year(self):
        return 2018

    @property
    def number(self):
        return 1

    @property
    def input_type(self):
        return InputTypes.INTARRAY

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

