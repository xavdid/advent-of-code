# prompt: https://adventofcode.com/2022/day/22

import re
from typing import Literal

from ...base import GridPoint, TextSolution, answer


def add(loc: GridPoint, offset: GridPoint) -> GridPoint:
    return tuple(a + b for a, b in zip(loc, offset))


OFFSETS = [(0, 1), (1, 0), (0, -1), (-1, 0)]


class Grid:
    offset_index = 0

    def __init__(self, raw_input: str) -> None:
        grid, path = raw_input.split("\n\n")

        self.grid, self.max_rows, self.max_cols = self.parse_grid(grid)
        self.path = self.parse_path(path)

        self.loc: GridPoint = 0, raw_input.find(".")

    def parse_grid(self, raw_grid: str) -> tuple[dict[tuple[int, int], bool], int, int]:
        rows = raw_grid.split("\n")
        max_rows = len(rows)
        max_cols = max(len(s) for s in rows)

        grid: dict[tuple[int, int], bool] = {}

        for row, line in enumerate(rows):
            for col, c in enumerate(line):
                if c == " ":
                    continue
                grid[(row, col)] = c == "."

        return grid, max_rows, max_cols

    def parse_path(self, s: str) -> list[Literal["L", "R"] | int]:
        directions = ("L", "R")
        return [c if c in directions else int(c) for c in re.findall(r"\d+|\w", s)]

    @property
    def offset(self):
        return OFFSETS[self.offset_index]

    def next_valid_loc(self):
        next_loc = add(self.loc, self.offset)
        while next_loc not in self.grid:
            # change next_loc to be in grid
            if next_loc[0] >= self.max_rows:
                next_loc = -1, next_loc[1]
            elif next_loc[1] >= self.max_cols:
                next_loc = next_loc[0], -1
            elif next_loc[0] < 0:
                next_loc = self.max_rows, next_loc[1]
            elif next_loc[1] < 0:
                next_loc = next_loc[0], self.max_cols

            next_loc = add(next_loc, self.offset)

        return next_loc

    def run(self):
        for ins in self.path:
            if ins == "L":
                self.offset_index = (self.offset_index - 1) % 4
            elif ins == "R":
                self.offset_index = (self.offset_index + 1) % 4
            else:
                for _ in range(ins):
                    if self.grid[next_loc := self.next_valid_loc()]:
                        self.loc = next_loc
                    else:
                        break

        return 1000 * (self.loc[0] + 1) + 4 * (self.loc[1] + 1) + self.offset_index


class Solution(TextSolution):
    _year = 2022
    _day = 22

    @answer(66292)
    def part_1(self) -> int:
        return Grid(self.input).run()

    # @answer(1234)
    def part_2(self) -> int:
        pass

    # @answer((1234, 4567))
    # def solve(self) -> tuple[int, int]:
    #     pass
