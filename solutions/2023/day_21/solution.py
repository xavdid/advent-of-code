# prompt: https://adventofcode.com/2023/day/21

from collections import deque
from typing import Callable

from ...base import StrSplitSolution, answer
from ...utils.graphs import GridPoint, neighbors, parse_grid


class Solution(StrSplitSolution):
    _year = 2023
    _day = 21

    @answer((3729, 621289922886149))
    def solve(self) -> tuple[int, int]:
        grid_size = len(self.input)
        grid = parse_grid(self.input, ignore_chars="#")
        plot_locations = set(grid)

        visited: dict[GridPoint, int] = {}
        queue: deque[tuple[int, GridPoint]] = deque(
            [(0, next(k for k, v in grid.items() if v == "S"))]
        )

        def num_points_where(f: Callable[[int], bool]) -> int:
            return sum(f(v) for v in visited.values())

        while queue:
            distance, point = queue.popleft()

            if point in visited:
                continue

            visited[point] = distance

            for n in neighbors(point, num_directions=4):
                if n in visited or n not in plot_locations:
                    continue

                queue.append((distance + 1, n))

        distance_to_edge = grid_size // 2
        assert (
            distance_to_edge == 65
        ), f"unexpected distance to edge, got {distance_to_edge}"

        part_1 = num_points_where(lambda v: v < distance_to_edge and v % 2 == 0)

        n = (26501365 - distance_to_edge) // grid_size
        assert n == 202300, f"n calc wrong, got {n}"
        num_odd_tiles = (n + 1) ** 2
        num_even_tiles = n**2

        odd_corners = num_points_where(lambda v: v > distance_to_edge and v % 2 == 1)
        even_corners = num_points_where(lambda v: v > distance_to_edge and v % 2 == 0)

        part_2 = (
            num_odd_tiles * num_points_where(lambda v: v % 2 == 1)
            + num_even_tiles * num_points_where(lambda v: v % 2 == 0)
            - ((n + 1) * odd_corners)
            + (n * even_corners)
        )

        return part_1, part_2
