# prompt: https://adventofcode.com/2021/day/15

from collections import defaultdict
from heapq import heappop, heappush
from itertools import product
from math import inf
from typing import DefaultDict, Dict, List, Set, Tuple

from ...base import StrSplitSolution, answer

Point = Tuple[int, int]


class Solution(StrSplitSolution):
    _year = 2021
    _day = 15

    def parse_grid(self, grid_mult: int) -> Tuple[Dict[Point, int], int, int]:
        max_x = len(self.input[0])
        max_y = len(self.input)
        grid: Dict[Point, int] = {}
        for y, line in enumerate(self.input):
            for x, val in enumerate(line):
                val = int(val)  # noqa: PLW2901
                for mult_x, mult_y in product(range(grid_mult), range(grid_mult)):
                    out = val + mult_x + mult_y
                    if out > 9:
                        out = out % 10 + 1

                    grid[(x + max_x * mult_x, y + max_y * mult_y)] = out

        return grid, max_x * grid_mult - 1, max_y * grid_mult - 1

    def _solve(self, grid_mult: int) -> int:
        grid, max_x, max_y = self.parse_grid(grid_mult)

        def neighbors(loc: Point) -> List[Point]:
            res = []
            x, y = loc
            for i, j in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                if not 0 <= x + i <= max_x:
                    continue

                if not 0 <= y + j <= max_y:
                    continue

                res.append((x + i, y + j))

            return res

        # Let's do a Dijkstra
        # https://en.wikipedia.org/wiki/Dijkstra%27s_algorithm

        target = (max_x, max_y)

        visited: Set[Point] = set()
        start: Point = (0, 0)
        distances: DefaultDict[Point, float] = defaultdict(lambda: inf, {start: 0})
        queue: List[Tuple[int, Tuple[int, int]]] = [(0, start)]

        while queue:
            distance, current = heappop(queue)

            if current in visited:
                continue

            if current == target:
                return distance

            visited.add(current)

            for n in neighbors(current):
                if n in visited:
                    continue

                potential_distance = distance + grid[n]

                if potential_distance < distances[n]:
                    distances[n] = potential_distance
                    heappush(queue, (potential_distance, n))

        return -1  # no path from start to target

    @answer((581, 2916))
    def solve(self) -> Tuple[int, int]:
        return self._solve(1), self._solve(5)
