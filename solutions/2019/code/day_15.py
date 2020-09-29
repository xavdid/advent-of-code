# prompt: https://adventofcode.com/2019/day/15

from .day_2 import IntcodeComputer, IntcodeSolution


class Solution(IntcodeSolution):
    year = 2019
    number = 15

    def part_1(self):
        computer = IntcodeComputer(self.input, debug=self.debug)
        while True:
            halted = computer.run(num_outputs=1)
            print(computer.output[-1])
            if halted:
                break

    def part_2(self):
        pass

    def solve(self):
        pass
