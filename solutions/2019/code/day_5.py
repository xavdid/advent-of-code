# prompt: https://adventofcode.com/2019/day/5

from ...base import BaseSolution, InputTypes
from .day_2 import IntcodeComputer


class Solution(BaseSolution):
    @property
    def year(self):
        return 2019

    @property
    def number(self):
        return 5

    @property
    def input_type(self):
        return InputTypes.INTSPLIT

    @property
    def separator(self):
        return ","

    def part_1(self):
        computer = IntcodeComputer(self.input, inputs=[1])
        computer.run()
        return computer.output

    def part_2(self):
        pass

    def solve(self):
        pass
