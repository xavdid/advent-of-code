# prompt: https://adventofcode.com/2024/day/8

from itertools import combinations

from ...base import StrSplitSolution, answer
from ...utils.graphs import add_points, parse_grid, subtract_points


class Solution(StrSplitSolution):
    _year = 2024
    _day = 8

    @answer(371)
    def part_1(self) -> int:
        grid = parse_grid(self.input)
        # ignore the space, but keep the grid dimensions
        frequencies = set(grid.values()) - {"."}

        antinode_locations = set()

        for frequency in frequencies:
            locations = (k for k, v in grid.items() if v == frequency)

            for l, r in combinations(locations, 2):
                slope = subtract_points(l, r)

                for p in add_points(l, slope), subtract_points(r, slope):
                    if p in grid:
                        antinode_locations.add(p)

        return len(antinode_locations)

    @answer(1229)
    def part_2(self) -> int:
        grid = parse_grid(self.input)
        # ignore the space, but keep the grid dimensions
        frequencies = set(grid.values()) - {"."}

        antinode_locations = set()

        for frequency in frequencies:
            locations = (k for k, v in grid.items() if v == frequency)

            for l, r in combinations(locations, 2):
                slope = subtract_points(l, r)

                for p, fn in (l, add_points), (r, subtract_points):
                    antinode_locations.add(p)

                    while (next_p := fn(p, slope)) in grid:
                        antinode_locations.add(next_p)
                        p = next_p  # noqa: PLW2901

        return len(antinode_locations)
