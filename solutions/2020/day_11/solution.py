# prompt: https://adventofcode.com/2020/day/11

from collections import Counter
from enum import Enum
from functools import cache  # pylint: disable=no-name-in-module
from typing import Generator, List

from ...base import BaseSolution, InputTypes

# inherit from str so it prints nicely
# class Tile(str, Enum):
#     FLOOR = "."
#     EMPTY_SEAT = "L"
#     OCCUPIED_SEAT = "#"


class Grid:
    def __init__(self, grid: List[str], change_threshold: int) -> None:
        self.grid = grid
        self.next_grid = []

        self.max_x = len(self.grid[0])
        self.max_y = len(self.grid)

        self.change_threshold = change_threshold

    @cache
    def tile_at(self, y, x) -> str:
        if y < 0 or x < 0 or x == self.max_x or y == self.max_y:
            return "."
        return self.grid[y][x]

    def adjacent_tiles(self, y, x):
        # clockwise from 12
        directions = [
            (y - 1, x),
            (y - 1, x + 1),
            (y, x + 1),
            (y + 1, x + 1),
            (y + 1, x),
            (y + 1, x - 1),
            (y, x - 1),
            (y - 1, x - 1),
        ]

        for direction in directions:
            yield self.tile_at(*direction)

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
    year = 2020
    number = 11
    input_type = InputTypes.STRSPLIT

    def part_1(self) -> int:
        grid = Grid(self.input, 4)

        while grid.step():
            pass

        return grid.count_tiles()["#"]

    def part_2(self) -> int:
        pass

    # def solve(self) -> Tuple[int, int]:
    #     pass
