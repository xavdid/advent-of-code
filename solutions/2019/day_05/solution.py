# prompt: https://adventofcode.com/2019/day/5

from ..intcode import IntcodeComputer, IntcodeSolution


class Solution(IntcodeSolution):
    _year = 2019
    _day = 5

    def part_1(self):
        computer = IntcodeComputer(self.input, inputs=[1])
        computer.run()
        return computer.diagnostic()

    def part_2(self):
        computer = IntcodeComputer(self.input, inputs=[5])
        computer.run()
        return computer.diagnostic()
