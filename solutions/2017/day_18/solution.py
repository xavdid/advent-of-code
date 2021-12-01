# prompt: https://adventofcode.com/2017/day/18

from ...base import BaseSolution, InputTypes
from string import ascii_lowercase


class TIS100:
    # this is shared across instances
    queues = {}

    def __init__(self, program, execution_mode, id_=None):
        self.registers = {l: 0 for l in ascii_lowercase}
        self.id = id_
        self.pos = 0
        self.last_sound = 0
        self.is_finished = False
        self.is_locked = False  # waiting to read from queue, used to track deadlocks

        self.program = program
        if execution_mode not in [1, 2]:
            raise ValueError("Execution mode must be either 1 or 2")
        self.execution_mode = execution_mode

        if execution_mode == 2:
            if id_ is None:
                raise ValueError("must supply an id")

            self.registers["p"] = id_
            self.queues[self.id] = []

    @property
    def is_halted(self):
        return self.is_locked or self.is_finished

    @property
    def queue(self):
        return self.queues[self.id]

    @property
    def destination(self):
        # could adjust this to work with more than 2 at a time
        return 1 - self.id

    def send(self, to, val):
        """
        send an outgoing value via the supplied function
        """
        if to not in self.queues:
            raise ValueError("unable to send to id", to)
        self.queues[to].append(val)

    def evaluate(self, r):
        """
        takes a register or a number and returns the integer value
        """
        if r in self.registers:
            return self.registers[r]
        else:
            return int(r)

    def execute(self):
        while not self.is_finished:
            self.step()

    def step(self):
        if self.is_finished:
            return

        if self.pos < 0 or self.pos >= len(self.program):
            self.is_finished = True
            return

        command, *instructions = self.program[self.pos].split(" ")

        if command == "snd":
            if self.execution_mode == 1:
                self.last_sound = self.evaluate(instructions[0])
            else:
                self.last_sound += 1
                self.send(self.destination, self.evaluate(instructions[0]))

        if command == "set":
            self.registers[instructions[0]] = self.evaluate(instructions[1])

        if command == "add":
            self.registers[instructions[0]] += self.evaluate(instructions[1])

        if command == "mul":
            self.registers[instructions[0]] *= self.evaluate(instructions[1])

        if command == "mod":
            self.registers[instructions[0]] %= self.evaluate(instructions[1])

        if command == "rcv":
            if self.execution_mode == 1:
                if self.evaluate(instructions[0]) != 0:
                    # we want the first recieved sound, so stop once we play one
                    self.is_finished = True
            else:
                if self.queue:
                    self.is_locked = False
                    self.registers[instructions[0]] = self.queue.pop(0)
                else:
                    self.is_locked = True
                    return

        if command == "jgz" and self.evaluate(instructions[0]) > 0:
            self.pos += self.evaluate(instructions[1])
            return  # don't increment position below

        self.pos += 1


class Solution(BaseSolution):
    _year = 2017
    _number = 18

    @property
    def input_type(self):
        return InputTypes.STRSPLIT

    def part_1(self):
        c = TIS100(self.input, 1)
        c.execute()
        return c.last_sound

    def part_2(self):
        c0 = TIS100(self.input, 2, 0)
        c1 = TIS100(self.input, 2, 1)

        while True:
            if c0.is_halted and c1.is_halted:
                break

            c0.step()
            c1.step()

        return c1.last_sound
