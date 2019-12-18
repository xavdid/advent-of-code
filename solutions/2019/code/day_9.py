# prompt: https://adventofcode.com/2019/day/9

from ...base import BaseSolution, InputTypes, slow
from .day_2 import IntcodeComputer


class Solution(BaseSolution):
    @property
    def year(self):
        return 2019

    @property
    def number(self):
        return 9

    @property
    def input_type(self):
        return InputTypes.INTSPLIT

    @property
    def separator(self):
        return ","

    def part_1(self):
        computer = IntcodeComputer(self.input, inputs=[1])
        computer.run()
        assert len(computer.output) == 1
        return computer.output[0]

    @slow
    def part_2(self):
        computer = IntcodeComputer(self.input, inputs=[2])
        computer.run()
        assert len(computer.output) == 1
        return computer.output[0]

    def solve(self):
        pass
