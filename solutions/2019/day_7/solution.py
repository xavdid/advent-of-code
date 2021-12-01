# prompt: https://adventofcode.com/2019/day/7

from itertools import cycle, permutations

from ..intcode import STOP_REASON, IntcodeComputer, IntcodeSolution


class Solution(IntcodeSolution):
    _year = 2019
    _number = 7

    def part_1(self):
        max_signal = -9999

        for sequence in permutations([0, 1, 2, 3, 4], 5):
            last_output = 0
            for setting in sequence:
                computer = IntcodeComputer(self.input, inputs=[setting, last_output])
                computer.run()
                last_output = computer.output[0]
            max_signal = max(max_signal, last_output)

        return max_signal

    def part_2(self):
        max_signal = -9999

        for sequence in permutations([5, 6, 7, 8, 9], 5):
            last_output = 0
            cpu = [
                IntcodeComputer(self.input, inputs=[setting]) for setting in sequence
            ]

            for computer in cycle(cpu):
                computer.add_input(last_output)
                finished = computer.run(num_outputs=1) == STOP_REASON.HALTED
                last_output = computer.output[-1]
                if finished:
                    # make sure to take the output of amplifier E
                    last_output = cpu[-1].output[-1]
                    break
            max_signal = max(max_signal, last_output)

        return max_signal

    def solve(self):
        pass
