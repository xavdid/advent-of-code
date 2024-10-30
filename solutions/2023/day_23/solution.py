# prompt: https://adventofcode.com/2023/day/23

from collections import defaultdict

from ...base import StrSplitSolution, answer, slow
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

    @slow
    @answer(6442)
    def part_2(self) -> int:
        grid = parse_grid(self.input, ignore_chars="#")

        start = next(p for p in grid if p[0] == 0)
        target = next(p for p in grid if p[0] == len(self.input) - 1)

        # build the grid as
        # { intersection => { other_intersection => distance } }

        # build graph

        paths: list[tuple[GridPoint, GridPoint]] = [(start, start)]
        graph: defaultdict[GridPoint, dict[GridPoint, int]] = defaultdict(dict)

        while paths:
            starting_point, cur = paths.pop()
            seen = {starting_point}

            while True:
                if cur == target:
                    graph[starting_point][cur] = len(seen)
                    break

                seen.add(cur)

                moves = [
                    n
                    for n in neighbors(cur, num_directions=4)
                    if n in grid and n not in seen
                ]

                if not moves:
                    break
                if len(moves) == 1:
                    cur = moves[0]
                    continue

                if cur not in graph[starting_point]:
                    # we started on the first step, so we have to offset by 1
                    graph[starting_point][cur] = len(seen) - 1
                    paths += [(cur, n) for n in moves]

                break

        # explore the grid
        stack: list[tuple[GridPoint, int, set[GridPoint]]] = [(start, 0, set())]
        distances: list[int] = []

        while stack:
            cur, distance, seen = stack.pop()

            if cur == target:
                distances.append(distance)
                continue

            seen.add(cur)

            for intersection, d in graph[cur].items():
                if intersection not in seen:
                    stack.append((intersection, distance + d, seen.copy()))

        return max(distances)
