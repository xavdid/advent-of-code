# prompt: https://adventofcode.com/2018/day/1

from itertools import cycle

from itertools import cycle
from ...base import BaseSolution, InputTypes


class Solution(BaseSolution):
    year = 2018
    number = 1

    @property
    def input_type(self):
        return InputTypes.INTSPLIT

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

