# prompt: https://adventofcode.com/2023/day/23

from heapq import heappop, heappush

from ...base import StrSplitSolution, answer
from ...utils.graphs import GridPoint, add_points, neighbors, parse_grid

OFFSETS = {
    ">": (0, 1),
    "v": (1, 0),
    "<": (0, -1),
    "^": (0, -1),
}


class Solution(StrSplitSolution):
    _year = 2023
    _day = 23

    @answer(2094)
    def part_1(self) -> int:
        grid = parse_grid(self.input, ignore_chars="#")

        start = next(p for p in grid if p[0] == 0)
        target = next(p for p in grid if p[0] == len(self.input) - 1)

        paths: list[tuple[GridPoint, set[GridPoint]]] = [(start, {start})]
        distances: list[int] = []

        while paths:
            cur, seen = paths.pop()

            while True:
                if cur == target:
                    distances.append(len(seen))
                    break

                seen.add(cur)

                if slide := OFFSETS.get(grid[cur]):
                    if (step := add_points(cur, slide)) not in seen:
                        moves = [step]
                    else:
                        moves = []
                else:
                    moves = [
                        n
                        for n in neighbors(cur, num_directions=4)
                        if n in grid and n not in seen
                    ]

                if len(moves) == 1:
                    cur = moves[0]
                else:
                    paths += [(n, seen.copy()) for n in moves]
                    break

        return max(distances)

    # @answer(1234)
    def part_2(self) -> int:
        pass

    # @answer((1234, 4567))
    # def solve(self) -> tuple[int, int]:
    #     pass
