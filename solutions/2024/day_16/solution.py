# prompt: https://adventofcode.com/2024/day/16

from heapq import heappop, heappush
from math import inf

from ...base import StrSplitSolution, answer
from ...utils.graphs import Direction, GridPoint, Position, parse_grid

type State = tuple[int, Position, tuple[GridPoint, ...]]


class Solution(StrSplitSolution):
    _year = 2024
    _day = 16

    @answer((98520, 609))
    def solve(self) -> tuple[int, int]:
        visited: set[Position] = set()
        best_seats: set[GridPoint] = set()
        lowest_cost = inf

        grid = parse_grid(self.input, ignore_chars="#")
        start = Position(next(k for k, v in grid.items() if v == "S"), Direction.RIGHT)
        queue: list[State] = [(0, start, (start.loc,))]

        while queue:
            cost, position, path = heappop(queue)

            if grid[position.loc] == "E" and cost <= lowest_cost:
                lowest_cost = cost
                best_seats |= set(path) | {position.loc}
                continue

            if lowest_cost < inf:
                break

            visited.add(position)

            next_pos = position.step()
            if next_pos.loc in grid and next_pos not in visited:
                heappush(queue, (cost + 1, next_pos, path + (position.loc,)))

            for direction in "CW", "CCW":
                if (next_pos := position.rotate(direction)) not in visited:
                    heappush(queue, (cost + 1000, next_pos, path))

        return int(lowest_cost), len(best_seats)
