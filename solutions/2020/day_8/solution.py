# prompt: https://adventofcode.com/2020/day/8

from dataclasses import dataclass
from enum import Enum
from typing import List, Set

from ...base import BaseSolution, InputTypes


class InfiniteLoopException(Exception):
    pass


class Operation(Enum):
    NOP = "nop"
    ACC = "acc"
    JMP = "jmp"


@dataclass
class Instruction:
    op: Operation
    # signed int
    arg: int


class VM:
    pointer: int = 0
    acc: int = 0

    def __init__(self, instructions: List[str]) -> None:
        # here so that it's not declared statically
        self.visited: Set[int] = set()
        self.instructions: List[Instruction] = []

        for i in instructions:
            op, arg = i.split(" ")
            self.instructions.append(Instruction(Operation(op), int(arg)))

    def run(self) -> None:
        while True:
            self.execute()
            # this should maybe be == len(...
            # > attempting to execute an instruction
            # > immediately after the last instruction in the file
            if self.pointer >= len(self.instructions):
                break

    def execute(self) -> None:
        ins = self.instructions[self.pointer]
        if self.pointer in self.visited:
            raise InfiniteLoopException()

        self.visited.add(self.pointer)

        if ins.op == Operation.NOP:
            self.pointer += 1

        elif ins.op == Operation.ACC:
            self.acc += ins.arg
            self.pointer += 1

        elif ins.op == Operation.JMP:
            self.pointer += ins.arg

        else:
            raise ValueError(f"unknown operator: {ins.op}")


class Solution(BaseSolution):
    _year = 2020
    _day = 8
    input_type = InputTypes.STRSPLIT

    def part_1(self) -> int:
        vm = VM(self.input)
        try:
            vm.run()
        except InfiniteLoopException:
            return vm.acc

    def part_2(self) -> int:
        # iterate over the input and change one input at a time
        for i in range(len(self.input)):
            if self.input[i].startswith("acc"):
                continue

            vm = VM(self.input)
            # swap the operation
            vm.instructions[i].op = (
                Operation.NOP
                if vm.instructions[i].op == Operation.JMP
                else Operation.JMP
            )

            try:
                vm.run()
            except InfiniteLoopException:
                continue

            return vm.acc
