# prompt: https://adventofcode.com/2021/day/25

from typing import Dict
from ...base import GridPoint, StrSplitSolution, TextSolution, answer

# from typing import Tuple
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

    # @answer(1234)
    def part_1(self) -> int:
        grid: Grid = {}
        row = col = 0
        for row, line in enumerate(self.input):
            for col, c in enumerate(line):
                if c == ".":
                    continue
                grid[row, col] = c

        self.max_row = row + 1
        self.max_col = col + 1

        # self.pp(grid)
        # self.pp("\ninitial")
        # if self.debug:
        # self.print_grid(grid)

        for i in range(999):
            next_grid: Grid = {}
            for (row, col), c in grid.items():
                if c == ">":
                    new_col = (col + 1) % self.max_col
                    # self.pp(f"checking if E {row, col} can move to {row, new_col}")
                    if (row, new_col) not in grid:
                        # self.pp("True!")
                        next_grid[row, new_col] = c
                    else:
                        # self.pp("False")
                        next_grid[row, col] = c

            for (row, col), c in grid.items():
                if c == "v":
                    new_row = (row + 1) % self.max_row
                    new_point = (new_row, col)
                    # self.pp(f"checking if S {row, col} can move to {new_row, col}")

                    # 1. check that no one moved into it
                    # 2. check that the old resident isn't a v
                    # check
                    can_move = new_point not in next_grid and grid.get(new_point) != "v"

                    if can_move:
                        # self.pp("True!")
                        next_grid[new_row, col] = c
                    else:
                        # self.pp("False")
                        next_grid[row, col] = c

            if grid == next_grid:
                return i + 1

            assert len(grid) == len(
                next_grid
            ), f"grid changed size from {len(grid)} to {len(next_grid)}"

            grid = next_grid

            # print(f"\nafter {i} steps")
            # self.print_grid(grid)

        raise ValueError("no solution")

    # @answer(1234)
    def part_2(self) -> int:
        pass

    # @answer((1234, 4567))
    # def solve(self) -> Tuple[int, int]:
    #     pass
