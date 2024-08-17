# prompt: https://adventofcode.com/2023/day/10

from math import ceil

from ...base import StrSplitSolution, answer
from ...utils.graphs import Grid, GridPoint, add_points, neighbors, parse_grid

OFFSETS = {
    "|": ((1, 0), (-1, 0)),
    "-": ((0, 1), (0, -1)),
    "L": ((-1, 0), (0, 1)),
    "J": ((-1, 0), (0, -1)),
    "7": ((0, -1), (1, 0)),
    "F": ((0, 1), (1, 0)),
}


def possible_moves(current: GridPoint, c: str) -> tuple[GridPoint, GridPoint]:
    res = tuple(add_points(current, o) for o in OFFSETS[c])
    assert len(res) == 2
    return res


def find_start_adjacent(grid: Grid, grid_size: int, start: GridPoint) -> GridPoint:
    result = []
    for neighbor in neighbors(start, 4, max_size=grid_size - 1, ignore_negatives=True):
        if grid[neighbor] == ".":
            continue

        if start in possible_moves(neighbor, grid[neighbor]):
            result.append(neighbor)

    assert (
        len(result) == 2
    ), f"didn't find exactly 2 points that could reach start: {result}"
    return result[0]


def interior_area(points: list[GridPoint]) -> float:
    padded_points = [*points, points[0]]  # form pair with last and first
    return (
        sum(
            row1 * col2 - row2 * col1
            for (row1, col1), (row2, col2) in zip(padded_points, padded_points[1:])
        )
        / 2
    )


class Solution(StrSplitSolution):
    _year = 2023
    _day = 10

    @answer((7005, 417))
    def solve(self) -> tuple[int, int]:
        # neighbors with a single max_size assumes a square grid, so ensure that
        assert len(self.input) == len(self.input[0]), "not a square grid!"

        grid = parse_grid(self.input)
        start = next(k for k, v in grid.items() if v == "S")
        points = [start]

        current = find_start_adjacent(grid, len(self.input), start)

        while True:
            last = points[-1]
            points.append(current)
            a, b = possible_moves(current, grid[current])

            if (start in (a, b)) and last != start:
                farthest_loop_distance = ceil(len(points) / 2)
                break

            current = a if b == last else b

        # shoelace - find the float area in a shape
        area = interior_area(points)

        # pick's theorem - find the number of points in a shape given its area
        num_interior_points = int(abs(area) - 0.5 * len(points) + 1)

        return farthest_loop_distance, num_interior_points
