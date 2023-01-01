# prompt: https://adventofcode.com/2022/day/18

from collections import defaultdict
from enum import Enum, auto
from itertools import product
from typing import Iterable

from ...base import StrSplitSolution, answer

GridPoint3D = tuple[int, int, int]


def neighbors_3d(p: GridPoint3D) -> Iterable[GridPoint3D]:
    for idx, offset in product(range(3), (-1, 1)):
        copied = list(p)
        copied[idx] += offset

        yield tuple(copied)


class PointState(Enum):
    UNREACHABLE = auto()
    ROCK = auto()
    REACHABLE = auto()


class Solution(StrSplitSolution):
    _year = 2022
    _day = 18

    def parse_points(self) -> set[GridPoint3D]:
        return {tuple(map(int, line.split(","))) for line in self.input}

    @answer(3466)
    def part_1(self) -> int:
        total = 0
        points = self.parse_points()

        for p in points:
            for neighbor in neighbors_3d(p):
                if neighbor not in points:
                    total += 1

        return total

    @answer(2012)
    def part_2(self) -> int:
        # return
        points = self.parse_points()

        grid: defaultdict[GridPoint3D, PointState] = defaultdict(
            lambda: PointState.UNREACHABLE
        )

        for p in points:
            grid[p] = PointState.ROCK

        size = 0
        for p in points:
            size = max(size, *p)
        size += 1  # grid that's 1 bigger than the biggest dimension

        seen: set[GridPoint3D] = set()
        queue: list[GridPoint3D] = [(0, 0, 0)]

        while queue:
            current = queue.pop()
            grid[current] = PointState.REACHABLE
            seen.add(current)

            for neighbor in neighbors_3d(current):
                if (
                    grid[neighbor] == PointState.UNREACHABLE
                    and neighbor not in seen
                    and all(-1 <= x <= size for x in neighbor)
                ):
                    queue.append(neighbor)

        total = 0
        for p in points:
            for neighbor in neighbors_3d(p):
                if grid[neighbor] == PointState.REACHABLE:
                    total += 1

        return total
