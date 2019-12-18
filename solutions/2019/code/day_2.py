# prompt: https://adventofcode.com/2019/day/2

from collections import defaultdict
from dataclasses import dataclass
from itertools import product
from typing import List

from ...base import BaseSolution, InputTypes


@dataclass
class Instruction:
    parameter: int
    mode: int


class IntcodeComputer:
    # pylint: disable=too-many-instance-attributes,no-self-use
    def __init__(self, program, inputs: List[int] = None):
        self.program = defaultdict(int)
        # used to be a list, now it's default dict so I can read from anywhere
        for index, i in enumerate(program):
            self.program[index] = i
        self.output = []
        self.pointer = 0
        self.valid_opcodes = set([1, 2, 3, 4, 5, 6, 7, 8, 9, 99])
        self.interactive = not inputs
        self.inputs = iter(inputs or [])
        self.relative_base = 0
        self.debug = False

    def get_input(self):
        if self.interactive:
            return int(input("--> "))
        return self.inputs.__next__()

    def add_input(self, val):
        # adds whatever we had before, no data lost
        self.inputs = iter([*list(self.inputs), val])

    def num_parameters(self, opcode: int):
        if opcode == 99:
            return 0
        if opcode in [1, 2, 7, 8]:
            return 3
        if opcode in [5, 6]:
            return 2
        if opcode in [3, 4, 9]:
            return 1
        raise ValueError("invalid opcode:", opcode)

    def parse_opcode(self, opcode: int):
        """
        Parse the 5-digit code
        Returns (opcode, mode, mode, mode), where everthing is an int
        """
        padded = str(opcode).zfill(5)
        return (int(padded[3:]), int(padded[2]), int(padded[1]), int(padded[0]))

    def slice_program(self, slice_range: range):
        return [self.program[x] for x in slice_range]

    def get_value(self, instruction: Instruction) -> int:
        """
        Dereferences an index based on mode
        """
        if instruction.mode == 0:  # position
            return self.program[instruction.parameter]
        if instruction.mode == 1:  # immediate
            return instruction.parameter
        if instruction.mode == 2:  # relative
            return self.program[self.relative_base + instruction.parameter]
        raise ValueError("invalid mode:", instruction)

    def get_write_value(self, instruction: Instruction) -> int:
        """
        Like `get_value`, but accounts for write instructions never uing immediate mode
        """
        if instruction.mode == 2:  # relative
            return instruction.parameter + self.relative_base
        # default is position
        return instruction.parameter

    def execute_opcode(self, opcode: int, params: List[Instruction]) -> bool:
        # we validate elsewhere, so we know we're good if we're here

        if self.debug:
            print("executing", opcode, params)

        # addition
        if opcode == 1:
            self.program[self.get_write_value(params[2])] = self.get_value(
                params[0]
            ) + self.get_value(params[1])
        # multiplication
        elif opcode == 2:
            self.program[self.get_write_value(params[2])] = self.get_value(
                params[0]
            ) * self.get_value(params[1])
        # input
        elif opcode == 3:
            self.program[self.get_write_value(params[0])] = self.get_input()
        # output
        elif opcode == 4:
            self.output.append(self.get_value(params[0]))
        # TJMP
        elif opcode == 5:
            if self.get_value(params[0]) != 0:
                self.pointer = self.get_value(params[1])
                return False
        # FJMP
        elif opcode == 6:
            if self.get_value(params[0]) == 0:
                self.pointer = self.get_value(params[1])
                return False
        # LT
        elif opcode == 7:
            res = 1 if self.get_value(params[0]) < self.get_value(params[1]) else 0
            self.program[self.get_write_value(params[2])] = res
        # EQ
        elif opcode == 8:
            res = 1 if self.get_value(params[0]) == self.get_value(params[1]) else 0
            self.program[self.get_write_value(params[2])] = res
        # mofify relative base
        elif opcode == 9:
            self.relative_base += self.get_value(params[0])

        return True  # increment pointer

    def run(self, single_output=False):
        num_outputs = len(self.output)
        while True:
            [opcode, *modes] = self.parse_opcode(self.program[self.pointer])
            if not opcode in self.valid_opcodes:
                raise ValueError(f"{opcode} is an invalid opcode")
            if opcode == 99:
                return True  # halted!

            num_params = self.num_parameters(opcode)

            params = [
                Instruction(param, modes[index])
                for index, param in enumerate(
                    self.slice_program(
                        range(self.pointer + 1, self.pointer + 1 + num_params)
                    )
                )
            ]

            if self.debug:
                print(self)

            should_increment_pointer = self.execute_opcode(opcode, params)

            if should_increment_pointer:
                self.pointer += num_params + 1

            if single_output and num_outputs != len(self.output):
                return False  # not yet halted

    def diagnostic(self):
        if not all([x == 0 for x in self.output[:-1]]):
            raise RuntimeError("bad diagnostic code", self.output[:-1])
        return self.output[-1]

    def __str__(self):
        # pylint: disable=line-too-long
        max_index = max(self.program)  # so empty items in the middle are accounted for
        return f"=======\nprogram: {[self.program[x] for x in range(max_index + 1)]}\npointer: {self.pointer}\nrelative_base: {self.relative_base}\noutput: {self.output}\n"


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

        raise RuntimeError("oh no")
