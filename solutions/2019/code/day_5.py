# prompt: https://adventofcode.com/2019/day/5

from .intcode import IntcodeComputer, IntcodeSolution


class Solution(IntcodeSolution):
    year = 2019
    number = 5

    def part_1(self):
        computer = IntcodeComputer(self.input, inputs=[1])
        computer.run()
        return computer.diagnostic()

    def part_2(self):
        computer = IntcodeComputer(self.input, inputs=[5])
        computer.run()
        return computer.diagnostic()

    def solve(self):
        pass
