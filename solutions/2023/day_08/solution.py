# prompt: https://adventofcode.com/2023/day/8

import math
import re
from itertools import cycle
from typing import Iterable

from ...base import TextSolution, answer


class Solution(TextSolution):
    _year = 2023
    _day = 8

    def _parse_input(self) -> tuple[Iterable[str], dict[str, dict[str, str]]]:
        raw_directions, raw_nodes = self.input.split("\n\n")

        instructions = cycle(raw_directions)

        nodes: dict[str, dict[str, str]] = {}
        for line in raw_nodes.split("\n"):
            root, l, r = re.findall(r"[A-Z]{3}", line)
            nodes[root] = {"L": l, "R": r}

        return instructions, nodes

    def _solve(self, current: str) -> int:
        instructions, nodes = self._parse_input()
        for idx, ins in enumerate(instructions):
            if current[-1] == "Z":
                return idx
            current = nodes[current][ins]

        return -1  # unreachable, but make type checker happy

    @answer(14681)
    def part_1(self) -> int:
        return self._solve("AAA")

    @answer(14321394058031)
    def part_2(self) -> int:
        _, nodes = self._parse_input()
        starts = [k for k in nodes.keys() if k[-1] == "A"]

        return math.lcm(*[self._solve(s) for s in starts])
