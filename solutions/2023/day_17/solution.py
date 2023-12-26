# prompt: https://adventofcode.com/2023/day/17

from heapq import heappop, heappush
from typing import NamedTuple

from ...base import StrSplitSolution, answer, slow
from ...utils.graphs import Direction, GridPoint, Rotation, add_points, parse_grid


class Position(NamedTuple):
    loc: GridPoint
    facing: Direction

    @property
    def next_loc(self) -> GridPoint:
        return add_points(self.loc, Direction.offset(self.facing))

    def step(self) -> "Position":
        return Position(self.next_loc, self.facing)

    def rotate_and_step(self, towards: Rotation):
        return Position(self.loc, Direction.rotate(self.facing, towards)).step()


# cost, position, number of steps in the same direction (max 3)
State = tuple[int, Position, int]


class Solution(StrSplitSolution):
    _year = 2023
    _day = 17

    def _solve(self, min_steps: int, max_steps: int) -> int:
        target = len(self.input) - 1, len(self.input[-1]) - 1
        grid = {k: int(v) for k, v in parse_grid(self.input).items()}

        queue: list[State] = [
            (0, Position((0, 0), Direction.DOWN), 0),
            (0, Position((0, 0), Direction.RIGHT), 0),
        ]
        seen: set[tuple[Position, int]] = set()

        while queue:
            cost, pos, num_steps = heappop(queue)

            if pos.loc == target and num_steps >= min_steps:
                return cost

            if (pos, num_steps) in seen:
                continue
            seen.add((pos, num_steps))

            if (
                num_steps >= min_steps
                and (left := pos.rotate_and_step("CCW")).loc in grid
            ):
                heappush(queue, (cost + grid[left.loc], left, 1))

            if (
                num_steps >= min_steps
                and (right := pos.rotate_and_step("CW")).loc in grid
            ):
                heappush(queue, (cost + grid[right.loc], right, 1))

            if num_steps < max_steps and (forward := pos.step()).loc in grid:
                heappush(queue, (cost + grid[forward.loc], forward, num_steps + 1))

        return -1

    @answer(1244)
    def part_1(self) -> int:
        return self._solve(0, 3)

    @slow
    @answer(1367)
    def part_2(self) -> int:
        return self._solve(4, 10)
