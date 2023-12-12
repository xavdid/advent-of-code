# prompt: https://adventofcode.com/2023/day/11

from itertools import combinations

from ...base import StrSplitSolution, answer
from ...utils.graphs import GridPoint, parse_grid, taxicab_distance


def empty_lines(grid: list[GridPoint], grid_size: int, dim: int) -> set[int]:
    return set(range(grid_size)) - {p[dim] for p in grid}


def expand_points(val: int, empty_lines: set[int], multiplier: int) -> int:
    return len(tuple(filter(lambda i: i < val, empty_lines))) * (multiplier - 1)


class Solution(StrSplitSolution):
    _year = 2023
    _day = 11

    def _solve(self, multiplier: int) -> int:
        assert len(self.input) == len(self.input[0]), "not a square grid!"
        grid_size = len(self.input)
        grid = list(parse_grid(self.input, ignore_chars=".").keys())

        rows_to_expand = empty_lines(grid, grid_size, dim=0)
        cols_to_expand = empty_lines(grid, grid_size, dim=1)

        expanded_points = {
            (
                row + expand_points(row, rows_to_expand, multiplier),
                col + expand_points(col, cols_to_expand, multiplier),
            )
            for row, col in grid
        }

        return sum(taxicab_distance(a, b) for a, b in combinations(expanded_points, 2))

    @answer(10289334)
    def part_1(self) -> int:
        return self._solve(2)

    @answer(649862989626)
    def part_2(self) -> int:
        return self._solve(1_000_000)
