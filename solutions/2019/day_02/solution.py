# prompt: https://adventofcode.com/2019/day/2

from itertools import product

from ..intcode import IntcodeComputer, IntcodeSolution


class Solution(IntcodeSolution):
    _year = 2019
    _day = 2

    def part_1(self):
        computer = IntcodeComputer(self.input)
        computer.program[1] = 12
        computer.program[2] = 2
        computer.run()
        return computer.program[0]

    def part_2(self):
        target = 19_690_720

        for noun, verb in product(range(100), range(100)):
            computer = IntcodeComputer(self.input)
            computer.program[1] = noun
            computer.program[2] = verb
            computer.run()
            result = computer.program[0]
            if result == target:
                return 100 * noun + verb

        raise RuntimeError("oh no")
