# prompt: https://adventofcode.com/2019/day/2

from operator import add, mul
from itertools import product
from ...base import BaseSolution, InputTypes


class Solution(BaseSolution):
    @property
    def year(self):
        return 2019

    @property
    def number(self):
        return 2

    @property
    def input_type(self):
        return InputTypes.INTSPLIT

    @property
    def separator(self):
        return ","

    def run_computer(self, noun=12, verb=2):
        program = self.input.copy()
        # initialize
        program[1] = noun
        program[2] = verb
        pointer = 0
        while True:
            opcode = program[pointer]
            # i don't think we can hit anything invalid here?
            if opcode == 99:
                break
            [a_index, b_index, dest_index] = program[pointer + 1 : pointer + 4]
            operation = add if opcode == 1 else mul  # will probably expand this
            program[dest_index] = operation(program[a_index], program[b_index])
            pointer += 4  # this may change

        return program[0]

    def part_1(self):
        return self.run_computer()

    def part_2(self):
        target = 19690720

        for noun, verb in product(range(0, 100), range(0, 100)):
            result = self.run_computer(noun=noun, verb=verb)
            if result == target:
                return 100 * noun + verb

        print("oh no")
