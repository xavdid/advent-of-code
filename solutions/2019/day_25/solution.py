# prompt: https://adventofcode.com/2019/day/25

import re
from collections import defaultdict
from itertools import combinations

from ...base import slow
from ..intcode import IntcodeComputer, IntcodeSolution
from .mem_dump import STATE

# these are unique to my input
ITEMS = (
    "jam",
    "loom",
    "mug",
    "spool of cat6",
    "prime number",
    "food ration",
    "fuel cell",
    "manifold",
)

FAIL_STR = "ejected"  # if this is in the latest output, we didn't pass


class Solution(IntcodeSolution):
    _year = 2019
    _number = 25

    def reset_computer(self):
        def fresh_state():
            return defaultdict(
                int,
                # state where i'm standing at the door with all items
                STATE,
            )

        computer = IntcodeComputer(self.input)
        computer.program = fresh_state()
        computer.pointer = 2663
        computer.relative_base = 4796

        return computer

    @slow
    def part_1(self):
        found = False
        computer = None
        for num_drops in range(1, 9):
            if found:
                break
            for drops in combinations(ITEMS, num_drops):
                computer = self.reset_computer()

                for drop in drops:
                    computer.add_input(f"drop {drop}")
                computer.add_input("north")

                computer.run(num_inputs=computer.num_queued_inputs)
                if FAIL_STR in "".join([chr(x) for x in computer.output]):
                    continue

                found = True
                break

        # computer is now inside the room! Dump the output
        if computer and found:
            res = computer.last_output_str()
            computer.flush_output()
            return re.search(r"\d{3,}", res).group()

        print("no combination found")

    def part_2(self):
        pass

    def solve(self):
        pass
