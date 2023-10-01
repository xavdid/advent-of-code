# prompt: https://adventofcode.com/2021/day/25

from typing import Callable, Dict, Tuple

from ...base import StrSplitSolution, answer
from ...utils.graphs import GridPoint

Grid = Dict[GridPoint, str]


class Solution(StrSplitSolution):
    _year = 2021
    _day = 25
    max_row: int
    max_col: int

    def print_grid(self, grid: Grid):
        for row in range(self.max_row):
            for col in range(self.max_col):
                print(grid.get((row, col), "."), end="")
            print()

    def parse_grid(self) -> Grid:
        grid: Grid = {}
        row = col = 0
        for row, line in enumerate(self.input):
            for col, c in enumerate(line):
                if c == ".":
                    continue
                grid[row, col] = c

        self.max_row = row + 1
        self.max_col = col + 1
        return grid

    def new_point(self, row: int, col: int, c: str) -> Tuple[int, int]:
        if c == ">":
            col = (col + 1) % self.max_col
        if c == "v":
            row = (row + 1) % self.max_row

        return row, col

    @answer(419)
    def part_1(self) -> int:
        grid = self.parse_grid()

        for i in range(999):
            # pylint: disable=cell-var-from-loop
            next_grid: Grid = {}

            def step(mode: str, can_move: Callable[[GridPoint], bool]):
                for (row, col), c in grid.items():
                    if c != mode:
                        continue
                    new_point = self.new_point(row, col, c)

                    if can_move(new_point):
                        next_grid[new_point] = c
                    else:
                        next_grid[row, col] = c

            step(">", lambda new_point: new_point not in grid)
            step(
                "v",
                lambda new_point: new_point not in next_grid
                and grid.get(new_point) != "v",
            )

            if grid == next_grid:
                return i + 1

            grid = next_grid

        raise ValueError("no solution")

    @answer(None)
    def part_2(self) -> None:
        pass
