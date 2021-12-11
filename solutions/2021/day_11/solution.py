# prompt: https://adventofcode.com/2021/day/11

from dataclasses import dataclass
from typing import Dict, Iterable, List, Tuple

from ...base import StrSplitSolution, answer

Location = Tuple[int, int]


@dataclass
class Point:
    val: int
    flashed: bool = False

    def reset(self):
        if self.val > 9:
            self.val = 0
            self.flashed = False


def neighbors(loc: Location) -> List[Location]:
    res = []
    row, col = loc
    for i in (-1, 0, 1):
        for j in (-1, 0, 1):
            if i == 0 and j == 0:
                continue  # skip self
            if not 0 <= row + i <= 9:
                continue

            if not 0 <= col + j <= 9:
                continue

            res.append((row + i, col + j))

    return res


def print_grid(grid: Dict[Location, Point]):
    for row in range(10):
        for col in range(10):
            print(grid[(row, col)].val, end="")
        print()


class Solution(StrSplitSolution):
    _year = 2021
    _day = 11

    @answer((1599, 418))
    def solve(self) -> Tuple[int, int]:
        # ingest grid
        grid: Dict[Location, Point] = {}
        for row in range(10):
            for col in range(10):
                grid[(row, col)] = Point(int(self.input[row][col]))

        num_flashes_100_steps = 0
        for step in range(1, 500):
            to_power: Iterable[Location] = grid.keys()

            while to_power:
                triggered: List[Location] = []
                for loc in to_power:
                    p = grid[loc]

                    p.val += 1
                    if p.val > 9 and not p.flashed:
                        p.flashed = True
                        if step <= 100:
                            num_flashes_100_steps += 1
                        triggered += neighbors(loc)

                to_power = triggered

            if all(p.flashed for p in grid.values()):
                return num_flashes_100_steps, step

            for p in grid.values():
                p.reset()

            if self.debug:
                print_grid(grid)

        return num_flashes_100_steps, -1
