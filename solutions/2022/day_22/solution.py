# prompt: https://adventofcode.com/2022/day/22

import re
from typing import Literal

from ...base import GridPoint, TextSolution, answer


def add(loc: GridPoint, offset: GridPoint) -> GridPoint:
    return tuple(a + b for a, b in zip(loc, offset))


class Solution(TextSolution):
    _year = 2022
    _day = 22

    def parse_path(self, s: str) -> list[Literal["L", "R"] | int]:
        directions = ("L", "R")
        return [c if c in directions else int(c) for c in re.findall(r"\d+|\w", s)]

    def parse_grid(self, raw_grid: str):
        rows = raw_grid.split("\n")
        max_cols = max(len(s) for s in rows)
        max_rows = len(rows)
        grid: dict[tuple[int, int], bool] = {}
        for row, line in enumerate(rows):
            for col, c in enumerate(line):
                if c == " ":
                    continue
                grid[(row, col)] = c == "."

        return grid, max_rows, max_cols

    def parse_input(self):
        grid, path = self.input.split("\n\n")
        return self.parse_grid(grid), self.parse_path(path)

    @answer(66292)
    def part_1(self) -> int:
        (grid, max_rows, max_cols), path = self.parse_input()
        loc = 0, self.input.find(".")

        offsets = [(0, 1), (1, 0), (0, -1), (-1, 0)]
        offset_index = 0

        for ins in path:
            self.pp(f"\nStanding at {loc}, facing {offset_index}; executing {ins}")
            if ins == "L":
                self.pp("  rotating L")
                offset_index = (offset_index - 1) % 4
            elif ins == "R":
                self.pp("  rotating R")
                offset_index = (offset_index + 1) % 4
            else:
                self.pp("  moving")
                for _ in range(ins):
                    next_loc = add(loc, offsets[offset_index])
                    self.pp(f"    trying to move to {next_loc}")
                    while next_loc not in grid:
                        self.pp("        out of grid")
                        # change next_loc to be in grid
                        if next_loc[0] >= max_rows:
                            self.pp("        looping row")
                            next_loc = -1, next_loc[1]
                        elif next_loc[1] >= max_cols:
                            self.pp("        looping col")
                            next_loc = next_loc[0], -1
                        elif next_loc[0] < 0:
                            self.pp("        looping -row")
                            next_loc = max_rows, next_loc[1]
                        elif next_loc[1] < 0:
                            self.pp("        looping -col")
                            next_loc = next_loc[0], max_cols

                        next_loc = add(next_loc, offsets[offset_index])
                        self.pp(f"      at {next_loc}")

                    if grid[next_loc]:
                        self.pp("      moving")
                        loc = next_loc
                    else:
                        self.pp("      wall! unable to move")
                        break

        return 1000 * (loc[0] + 1) + 4 * (loc[1] + 1) + offset_index

    # @answer(1234)
    def part_2(self) -> int:
        pass

    # @answer((1234, 4567))
    # def solve(self) -> tuple[int, int]:
    #     pass
