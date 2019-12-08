# prompt: https://adventofcode.com/2019/day/2

from dataclasses import dataclass
from itertools import product
from typing import List

from ...base import BaseSolution, InputTypes


@dataclass
class Instruction:
    parameter: int
    mode: int


class IntcodeComputer:
    def __init__(self, program, inputs=None):
        self.program = program.copy()  # start fresh every time
        self.output = []
        self.pointer = 0
        self.valid_opcodes = set([0, 1, 2, 3, 4, 99])
        self.inputs = iter(inputs or [])

    def get_input(self):
        return self.inputs.__next__()

    def num_parameters(self, opcode: int):
        if opcode in [1, 2]:
            return 3
        if opcode == 99:
            return 0
        if opcode in [3, 4]:
            return 1

    def parse_opcode(self, opcode: int):
        """
        Parse the 5-digit code
        Returns (opcode, mode, mode, mode), where everthing is an int
        """
        padded = str(opcode).zfill(5)
        return (int(padded[3:]), int(padded[2]), int(padded[1]), int(padded[0]))

    def get_value(self, instruction: Instruction) -> int:
        if instruction.mode == 0:
            return self.program[instruction.parameter]
        if instruction.mode == 1:
            return instruction.parameter
        raise ValueError("Invalid param mode")

    def execute_opcode(self, opcode: int, params: List[Instruction]):
        if opcode == 1:
            # not getting value for this index could be wrong
            # though i think it's special since it's a write instruction
            self.program[params[2].parameter] = self.get_value(
                params[0]
            ) + self.get_value(params[1])
        elif opcode == 2:
            # not getting value for this index could be wrong
            # though i think it's special since it's a write instruction
            self.program[params[2].parameter] = self.get_value(
                params[0]
            ) * self.get_value(params[1])
        elif opcode == 3:
            # is this right?
            self.program[params[0].parameter] = self.get_input()
        elif opcode == 4:
            self.output.append(self.get_value(params[0]))

    def run(self):
        while True:
            [opcode, *modes] = self.parse_opcode(self.program[self.pointer])
            if not opcode in self.valid_opcodes:
                raise ValueError(f"{opcode} is an invalid opcode")
            if opcode == 99:
                break

            num_params = self.num_parameters(opcode)

            params = [
                Instruction(param, modes[index])
                for index, param in enumerate(
                    self.program[self.pointer + 1 : self.pointer + 1 + num_params]
                )
            ]

            self.execute_opcode(opcode, params)

            self.pointer += num_params + 1

    def __str__(self):
        return str(self.program)


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

    def part_1(self):
        computer = IntcodeComputer(self.input)
        computer.program[1] = 12
        computer.program[2] = 2
        computer.run()
        return computer.program[0]

    def part_2(self):
        target = 19_690_720

        for noun, verb in product(range(0, 100), range(0, 100)):
            computer = IntcodeComputer(self.input)
            computer.program[1] = noun
            computer.program[2] = verb
            computer.run()
            result = computer.program[0]
            if result == target:
                return 100 * noun + verb

        print("oh no")
