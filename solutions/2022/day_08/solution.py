# prompt: https://adventofcode.com/2022/day/8

# from typing import Tuple
from typing import List, Tuple

from ...base import StrSplitSolution, answer


class Solution(StrSplitSolution):
    _year = 2022
    _day = 8

    grid: List[List[int]] = []

    def parse_grid(self) -> int:
        self.grid = [[int(i) for i in row] for row in self.input]
        assert len(self.grid) == len(self.grid[0]), "not a square grid"
        return len(self.grid)

    def is_visible_from_above(self, row: int, col: int) -> Tuple[bool, int]:
        i = -100
        for i, look_row in enumerate(range(row - 1, -1, -1)):
            if self.grid[look_row][col] >= self.grid[row][col]:
                return False, i
        return True, i

    def is_visible_from_below(self, row: int, col: int) -> Tuple[bool, int]:
        i = -100
        for i, look_row in enumerate(range(row + 1, len(self.grid))):
            if self.grid[look_row][col] >= self.grid[row][col]:
                return False, i
        return True, i

    def is_visible_from_left(self, row: int, col: int) -> Tuple[bool, int]:
        i = -100
        for i, other_tree in enumerate(reversed(self.grid[row][:col])):
            if other_tree >= self.grid[row][col]:
                return False, i
        return True, i

    def is_visible_from_right(self, row: int, col: int) -> Tuple[bool, int]:
        i = -100
        for i, other_tree in enumerate(self.grid[row][col + 1 :]):
            if other_tree >= self.grid[row][col]:
                return False, i
        return True, i

    def is_visible(self, row: int, col: int) -> Tuple[bool, int]:
        is_visible = False
        result = 1
        for func in (
            self.is_visible_from_above,
            self.is_visible_from_right,
            self.is_visible_from_below,
            self.is_visible_from_left,
        ):
            visible, dist = func(row, col)
            is_visible = is_visible or visible
            result *= dist + 1

        return is_visible, result

    @answer((1820, 385112))
    def solve(self) -> Tuple[int, int]:
        grid_size = self.parse_grid()

        # the size of the border
        num_visible_trees = grid_size * 2 + (grid_size - 2) * 2

        best_view = 0

        for row in range(1, grid_size - 1):
            for col in range(1, grid_size - 1):
                if self.grid[row][col] == 0:
                    continue  # 0s are never visible and never the best tree
                visible, view_score = self.is_visible(row, col)
                num_visible_trees += visible
                best_view = max(best_view, view_score)

        return num_visible_trees, best_view
