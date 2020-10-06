# prompt: https://adventofcode.com/2019/day/9

from ...base import slow
from .intcode import IntcodeComputer, IntcodeSolution


class Solution(IntcodeSolution):
    year = 2019
    number = 9

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
