# prompt: https://adventofcode.com/2019/day/23

from typing import Optional, Tuple

from ..intcode import STOP_REASON, IntcodeComputer, IntcodeSolution


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
        vms = [
            IntcodeComputer(self.input, inputs=[address], default_input=-1)
            for address in range(50)
        ]

        nat_mem: Optional[Tuple[int, int]] = None
        last_sent: Optional[Tuple[int, int]] = None

        while True:
            # pylint: disable=invalid-name
            for vm in vms:
                stopped_reason = vm.run(num_outputs=3, num_inputs=1)

                if stopped_reason == STOP_REASON.NUM_INPUT:
                    # stopped because we took an input, don't look for output
                    continue

                to, x, y = vm.output[-3:]

                if to == 255:
                    nat_mem = (x, y)
                else:
                    vms[to].add_input([x, y])

            if all([vm.idle for vm in vms]):
                # network is idle, send the special packet to 0
                vms[0].add_input(nat_mem)

                # pylint: disable=unsubscriptable-object
                if last_sent and last_sent[1] == nat_mem[1]:
                    return nat_mem[1]

                last_sent = nat_mem
