# prompt: https://adventofcode.com/2022/day/19

import re
from typing import TypedDict

from ...base import StrSplitSolution, answer


class Ore(TypedDict):
    ore: int


class Obsidian(TypedDict):
    ore: int
    clay: int


class Geode(TypedDict):
    ore: int
    obsidian: int


class Blueprint(TypedDict):
    ore: Ore
    clay: Ore
    obsidian: Obsidian
    geode: Geode


class Solution(StrSplitSolution):
    _year = 2022
    _day = 19

    # @answer(1234)
    def part_1(self) -> int:
        blueprints: list[Blueprint] = []
        for line in self.input:
            costs = list(map(int, re.findall(r"(\d+) ", line)))
            blueprints.append(
                {
                    "ore": {"ore": costs[0]},
                    "clay": {"ore": costs[1]},
                    "obsidian": {"ore": costs[2], "clay": costs[3]},
                    "geode": {"ore": costs[4], "obsidian": costs[5]},
                }
            )

    # @answer(1234)
    def part_2(self) -> int:
        pass

    # @answer((1234, 4567))
    # def solve(self) -> tuple[int, int]:
    #     pass
