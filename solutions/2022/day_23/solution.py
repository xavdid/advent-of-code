# prompt: https://adventofcode.com/2022/day/23

from collections import defaultdict
from operator import itemgetter
from typing import Optional

from ...base import TextSolution, answer, slow
from ...utils.graphs import GridPoint, neighbors


def calculate_offset(tile: GridPoint, offset: GridPoint) -> GridPoint:
    return tuple(map(sum, zip(tile, offset)))


OFFSETS: dict[str, list[tuple[int, int]]] = {
    "N": [(-1, -1), (-1, 0), (-1, 1)],
    "E": [(-1, 1), (0, 1), (1, 1)],
    "S": [(1, 1), (1, 0), (1, -1)],
    "W": [(1, -1), (0, -1), (-1, -1)],
}


class Grid:
    directions = ["N", "S", "W", "E"]

    def __init__(self, raw_grid: str) -> None:
        self.grid: set[GridPoint] = set()

        for row, line in enumerate(raw_grid.split("\n")):
            for col, c in enumerate(line):
                if c == "#":
                    self.grid.add((row, col))

    def check_direction(self, elf: GridPoint, d: str) -> Optional[GridPoint]:
        """
        returns the move destination if there are no elves in the 3 points in `direction` from `elf`
        """
        if not any(calculate_offset(elf, o) in self.grid for o in OFFSETS[d]):
            return calculate_offset(elf, OFFSETS[d][1])

    def step(self) -> bool:
        # map of a position and who all wants to move there
        potential_moves: defaultdict[GridPoint, list[GridPoint]] = defaultdict(list)

        for elf in self.grid:
            # elves with no neighbors don't move
            if not any(n in self.grid for n in neighbors(elf)):
                continue

            for d in self.directions:
                if new_position := self.check_direction(elf, d):
                    potential_moves[new_position].append(elf)
                    break

        for destination, applicants in potential_moves.items():
            if len(applicants) > 1:
                continue

            self.grid.remove(applicants[0])
            self.grid.add(destination)

        # rotate list
        self.directions = self.directions[1:] + [self.directions[0]]

        return bool(potential_moves)

    def print_grid(self):
        min_row, max_row, min_col, max_col = self.get_corners()

        for r in range(min_row - 1, max_row + 2):
            for c in range(min_col - 1, max_col + 2):
                print("#" if (r, c) in self.grid else ".", end="")
            print()

    def get_area(self) -> int:
        min_row, max_row, min_col, max_col = self.get_corners()

        grid_size = (max_row - min_row + 1) * (max_col - min_col + 1)
        return grid_size - len(self.grid)

    def get_corners(self):
        min_row: int = min(map(itemgetter(0), self.grid))
        max_row: int = max(map(itemgetter(0), self.grid))

        min_col: int = min(map(itemgetter(1), self.grid))
        max_col: int = max(map(itemgetter(1), self.grid))

        return min_row, max_row, min_col, max_col


class Solution(TextSolution):
    _year = 2022
    _day = 23

    @slow
    @answer((4218, 976))
    def solve(self) -> tuple[int, int]:
        grid = Grid(self.input)

        part_1 = 0
        part_2 = 0

        for r in range(1, 1000):
            any_moves = grid.step()
            if r == 10:
                part_1 = grid.get_area()

            if not any_moves:
                part_2 = r
                break

        return part_1, part_2
