from collections import defaultdict
from dataclasses import dataclass
from enum import Enum, IntEnum, auto
from typing import List, Optional, Tuple, Union

from ..base import BaseSolution, InputTypes


class OPCODES(IntEnum):
    ADDITION = 1
    MULTIPLICATION = 2
    INPUT = 3
    OUTPUT = 4
    TJMP = 5
    FJMP = 6
    LT = 7
    EQ = 8
    RELATIVE_BASE = 9
    HALT = 99


class STOP_REASON(Enum):
    HALTED = auto()
    NUM_OUTPUT = auto()
    NUM_INPUT = auto()


@dataclass
class Instruction:
    parameter: int
    mode: int


class IntcodeComputer:
    # pylint: disable=too-many-instance-attributes,no-self-use
    def __init__(
        self, program, inputs: List[int] = None, debug=False, default_input=None
    ):
        self.program = defaultdict(int)
        # used to be a list, now it's default dict so I can read from anywhere
        for index, i in enumerate(program):
            self.program[index] = i
        self.output = []
        self.pointer = 0
        self.relative_base = 0

        self.num_queued_inputs = 0
        self.inputs = iter([])

        self.add_input(inputs or [])
        # the default value when there's no input and we try to read
        self.default_input = default_input

        self.last_output = 0

        self.debug = debug

        self.idle = False

    def copy(self):
        res = IntcodeComputer([])
        res.program = self.program.copy()
        res.inputs = iter([*list(self.inputs)])
        res.output = self.output.copy()
        res.pointer = self.pointer
        res.relative_base = self.relative_base
        res.debug = self.debug

        # missing some copy properties that weren't relevant at the time

        return res

    def get_input(self):
        if self.num_queued_inputs == 0:
            if self.default_input is None:
                input_ = None
                try:
                    input_ = input("--> ")
                    return int(input_)
                except ValueError:
                    # got ascii string input
                    if input_ == "SELF_DUMP":
                        print(self.pointer, self.relative_base)
                    self.add_input([ord(c) for c in f"{input_}\n"])
                    return self.get_input()
            else:
                self.idle = True
                return self.default_input

        self.num_queued_inputs -= 1
        self.idle = False
        return next(self.inputs)

    def add_input(self, val: Union[int, List[int], Tuple[int, ...], str]):
        self.idle = False
        if isinstance(val, (list, tuple)):
            for i in val:
                self.add_input(i)
        elif isinstance(val, int):
            self.num_queued_inputs += 1
            # adds whatever we had before, no data lost
            self.inputs = iter([*list(self.inputs), val])
        elif isinstance(val, str):
            self.add_input([ord(c) for c in f"{val}\n"])
        else:
            raise TypeError("Provide an int, an array of int, or a tuple of int")

    def num_parameters(self, opcode: int):
        if opcode == OPCODES.HALT:
            return 0
        if opcode in [OPCODES.ADDITION, OPCODES.MULTIPLICATION, OPCODES.LT, OPCODES.EQ]:
            return 3
        if opcode in [OPCODES.TJMP, OPCODES.FJMP]:
            return 2
        if opcode in [OPCODES.INPUT, OPCODES.OUTPUT, OPCODES.RELATIVE_BASE]:
            return 1
        raise ValueError("invalid opcode:", opcode)

    def parse_opcode(self, opcode: int) -> Tuple[int, int, int, int]:
        """
        Parse the 5-digit code
        Returns (opcode, mode, mode, mode)
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

    def execute_opcode(
        self, opcode: int, params: List[Instruction], flush=None
    ) -> Optional[bool]:
        """
        returns a boolean communicating whether the pointer should be incremented
        (not all instructions increment the pointer)
        flush prints all new output before each input
        """
        # we validate elsewhere, so we know we're good if we're here

        if self.debug:
            print("executing", opcode, params)

        if opcode == OPCODES.ADDITION:
            self.program[self.get_write_value(params[2])] = self.get_value(
                params[0]
            ) + self.get_value(params[1])
        elif opcode == OPCODES.MULTIPLICATION:
            self.program[self.get_write_value(params[2])] = self.get_value(
                params[0]
            ) * self.get_value(params[1])
        elif opcode == OPCODES.INPUT:
            if flush:
                self.flush_output()
            self.program[self.get_write_value(params[0])] = self.get_input()
        elif opcode == OPCODES.OUTPUT:
            self.output.append(self.get_value(params[0]))
        elif opcode == OPCODES.TJMP:
            if self.get_value(params[0]) != 0:
                self.pointer = self.get_value(params[1])
                return False
        elif opcode == OPCODES.FJMP:
            if self.get_value(params[0]) == 0:
                self.pointer = self.get_value(params[1])
                return False
        elif opcode == OPCODES.LT:
            res = 1 if self.get_value(params[0]) < self.get_value(params[1]) else 0
            self.program[self.get_write_value(params[2])] = res
        elif opcode == OPCODES.EQ:
            res = 1 if self.get_value(params[0]) == self.get_value(params[1]) else 0
            self.program[self.get_write_value(params[2])] = res
        elif opcode == OPCODES.RELATIVE_BASE:
            self.relative_base += self.get_value(params[0])

        return True  # increment pointer

    def run(self, num_outputs=None, num_inputs=None, flush=False) -> STOP_REASON:
        """
        * num_output pauses execution after a certain number of outputs has been generated
        * num_inputs pauses after a certain number of input instructions has happened
            helpful for syncinc up many vms
        """
        limit_outputs = bool(num_outputs)
        original_num_outputs = len(self.output)  # track how many we've gotten

        limit_inputs = bool(num_inputs)
        inputs_count = 0

        while True:
            [opcode, *modes] = self.parse_opcode(self.program[self.pointer])
            OPCODES(opcode)  # throws for invalid opcodes
            if opcode == OPCODES.HALT:
                if flush:
                    self.flush_output()
                return STOP_REASON.HALTED

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

            if opcode == OPCODES.INPUT and limit_inputs:
                if inputs_count == num_inputs:
                    return STOP_REASON.NUM_INPUT
                inputs_count += 1

            should_increment_pointer = self.execute_opcode(opcode, params, flush=flush)

            if should_increment_pointer:
                self.pointer += num_params + 1

            if limit_outputs and len(self.output) - original_num_outputs == num_outputs:
                return STOP_REASON.NUM_OUTPUT  # not yet halted

    def last_output_str(self):
        return "".join([chr(x) for x in self.output[self.last_output :]])

    def flush_output(self):
        """
        prints all output (in ascii format) since last flush
        """
        print(self.last_output_str())
        self.last_output = len(self.output)

    def diagnostic(self):
        if not all([x == 0 for x in self.output[:-1]]):
            raise RuntimeError("bad diagnostic code", self.output[:-1])
        return self.output[-1]

    def __str__(self):
        # pylint: disable=line-too-long
        max_index = max(self.program)  # so empty items in the middle are accounted for
        return f"=======\nprogram: {[self.program[x] for x in range(max_index + 1)]}\npointer: {self.pointer}\nrelative_base: {self.relative_base}\noutput: {self.output}\n"


class IntcodeSolution(BaseSolution):
    @property
    def input_type(self):
        return InputTypes.INTSPLIT

    @property
    def separator(self):
        return ","
