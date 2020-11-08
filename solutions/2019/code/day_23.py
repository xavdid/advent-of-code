# prompt: https://adventofcode.com/2019/day/23

from typing import Optional, Tuple

from .intcode import IntcodeComputer, IntcodeSolution


class Solution(IntcodeSolution):
    year = 2019
    number = 23

    def part_1(self):
        vms = [
            IntcodeComputer(self.input, inputs=[address], default_input=-1)
            for address in range(50)
        ]

        while True:
            # pylint: disable=invalid-name
            for vm in vms:
                vm.run(num_outputs=3, num_inputs=1)
                maybe_output: Optional[Tuple[int, int, int]] = vm.output[-3:]
                if not maybe_output:
                    continue
                to, x, y = maybe_output
                if to == 255:
                    return y

                vms[to].add_input([x, y])

    def part_2(self):
        pass

    def solve(self):
        pass
