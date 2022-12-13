# prompt: https://adventofcode.com/2022/day/12

from collections import defaultdict
from heapq import heappop, heappush

from ...base import GridPoint, StrSplitSolution, answer, neighbors


def can_step(src: str, dst: str) -> bool:
    if dst == "E":
        dst = "z"

    if src == "S":
        src = "a"

    return ord(src) + 1 >= ord(dst)


class Solution(StrSplitSolution):
    _year = 2022
    _day = 12

    grid: list[list[str]] = []

    def find_letters(self, letter: str):
        for row, line in enumerate(self.grid):
            for col, c in enumerate(line):
                if c == letter:
                    yield row, col

    def _solve(self, start: GridPoint) -> int:
        num_rows = len(self.grid) - 1
        num_cols = len(self.grid[0]) - 1

        visited: set[GridPoint] = set()
        distances = defaultdict(lambda: 10_000)

        queue: list[tuple[int, GridPoint]] = [(0, start)]

        while queue:
            distance, current = heappop(queue)
            src = self.grid[current[0]][current[1]]

            if src == "E":
                return distance

            if current in visited:
                continue

            visited.add(current)

            new_distance = distance + 1

            for n in neighbors(
                current,
                4,
                ignore_negatives=True,
                max_x_size=num_rows,
                max_y_size=num_cols,
            ):
                if n in visited:
                    continue

                if not can_step(src, self.grid[n[0]][n[1]]):
                    continue

                if new_distance < distances[n]:
                    distances[n] = new_distance
                    heappush(queue, (new_distance, n))

        return -1  # no path found

    @answer((408, 399))
    def solve(self) -> tuple[int, int]:
        self.grid = [list(l) for l in self.input]

        shortest_path_from_start = self._solve(next(self.find_letters("S")))

        shortest_path = min(
            filter(
                lambda x: x >= 0, (self._solve(loc) for loc in self.find_letters("a"))
            )
        )

        return shortest_path_from_start, shortest_path
