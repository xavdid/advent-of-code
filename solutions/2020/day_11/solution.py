# prompt: https://adventofcode.com/2020/day/11

from collections import Counter
from functools import cache  # pylint: disable=no-name-in-module
from typing import List, Tuple

from ...base import BaseSolution, InputTypes

SEATS = {"L", "#"}
# clockwise from 12
ADJACENT_POINTS = ("N", "NE", "E", "SE", "S", "SW", "W", "NW")


def point_from_heading(heading: str, y: int, x: int) -> Tuple[int, int]:
    if "N" in heading:
        y -= 1
    if "S" in heading:
        y += 1
    if "W" in heading:
        x -= 1
    if "E" in heading:
        x += 1

    return y, x


class Grid:
    def __init__(
        self, grid: List[str], change_threshold: int, ranged_adjacency=False
    ) -> None:
        self.grid = grid
        self.next_grid = []

        self.max_x = len(self.grid[0])
        self.max_y = len(self.grid)

        self.change_threshold = change_threshold
        self.ranged_adjacency = ranged_adjacency

    @cache
    def tile_at(self, y, x, heading=None) -> str:
        if y < 0 or x < 0 or x == self.max_x or y == self.max_y:
            return "."

        tile = self.grid[y][x]

        if tile in SEATS:
            return tile

        if heading:
            return self.tile_at(*point_from_heading(heading, y, x), heading=heading)

        return tile

    def adjacent_tiles(self, y, x):
        for heading in ADJACENT_POINTS:
            point = point_from_heading(heading, y, x)
            if self.ranged_adjacency:
                yield self.tile_at(*point, heading=heading)
            else:
                yield self.tile_at(*point)

    def next_tile(self, y, x) -> str:
        tile = self.grid[y][x]
        if tile == ".":
            return "."

        num_occupied_adjacent = 0
        for adj_tile in self.adjacent_tiles(y, x):
            if adj_tile == "#":
                # it has to have 0 to change from empty, so we can bail early
                if tile == "L":
                    return "L"

                num_occupied_adjacent += 1
                # stop as soon as we hit the treshold
                if num_occupied_adjacent == self.change_threshold and tile == "#":
                    return "L"

        # at this point, it's either an empty that has no occupieds next to it,
        # or an occupied that didn't meet threshold
        return "#"

    def print_grid(self):
        print()
        print("\n".join(["".join(row) for row in self.grid]))

    def count_tiles(self):
        res = Counter()
        for row in self.grid:
            res.update(row)
        return res

    def step(self) -> bool:
        """
        Returns `True` if further steps are needed, `False` otherwise
        """
        for y in range(self.max_y):
            new_row = []
            for x in range(self.max_x):
                new_row.append(self.next_tile(y, x))
            self.next_grid.append(new_row)

        if self.grid == self.next_grid:
            return False

        self.grid = self.next_grid
        self.next_grid = []
        self.tile_at.cache_clear()  # pylint: disable=no-member
        return True


class Solution(BaseSolution):
    _year = 2020
    _number = 11
    input_type = InputTypes.STRSPLIT

    def part_1(self) -> int:
        grid = Grid(self.input, 4)

        while grid.step():
            pass

        return grid.count_tiles()["#"]

    def part_2(self) -> int:
        grid = Grid(self.input, 5, ranged_adjacency=True)

        while grid.step():
            pass

        return grid.count_tiles()["#"]
