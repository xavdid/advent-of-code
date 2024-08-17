# prompt: https://adventofcode.com/2023/day/16

from functools import cache
from typing import NamedTuple

from ...base import StrSplitSolution, answer
from ...utils.graphs import Direction, Grid, GridPoint, Rotation, add_points, parse_grid


class State(NamedTuple):
    loc: GridPoint
    facing: Direction

    @property
    def next_loc(self) -> GridPoint:
        return add_points(self.loc, Direction.offset(self.facing))

    def step(self) -> "State":
        return State(self.next_loc, self.facing)

    def rotate_and_step(self, towards: Rotation):
        return State(self.loc, Direction.rotate(self.facing, towards)).step()

    @cache
    def next_states(self, char: str) -> list["State"]:
        match char:
            case ".":
                return [self.step()]
            # ignore the pointy end of a splitter
            case "-" if self.facing in (Direction.LEFT, Direction.RIGHT):
                return [self.step()]
            case "|" if self.facing in (Direction.UP, Direction.DOWN):
                return [self.step()]
            # split on splitters we didn't pass over
            case "-" | "|":
                return [
                    self.rotate_and_step("CCW"),
                    self.rotate_and_step("CW"),
                ]
            # bounce off mirrors
            case "/" if self.facing in (Direction.LEFT, Direction.RIGHT):
                return [self.rotate_and_step("CCW")]
            case "\\" if self.facing in (Direction.LEFT, Direction.RIGHT):
                return [self.rotate_and_step("CW")]
            case "/" if self.facing in (Direction.UP, Direction.DOWN):
                return [self.rotate_and_step("CW")]
            case "\\" if self.facing in (Direction.UP, Direction.DOWN):
                return [self.rotate_and_step("CCW")]
            case _:
                raise ValueError(
                    f"Unable to calculate next step from {self} and {char=}"
                )


class Solution(StrSplitSolution):
    _year = 2023
    _day = 16

    def _solve(self, grid: Grid, start: State) -> int:
        seen: set[State] = set()
        queue: list[State] = [start]

        while queue:
            current = queue.pop()
            if current in seen:
                continue
            seen.add(current)

            for next_state in current.next_states(grid[current.loc]):
                if next_state.loc in grid:
                    queue.append(next_state)  # noqa: PERF401

        return len({state.loc for state in seen})

    @answer(7884)
    def part_1(self) -> int:
        grid = parse_grid(self.input)
        return self._solve(grid, State((0, 0), Direction.RIGHT))

    @answer(8185)
    def part_2(self) -> int:
        grid = parse_grid(self.input)

        assert len(self.input) == len(self.input[0]), "not a square grid!"
        grid_size = len(self.input)

        return max(
            # top, facing down
            *(
                self._solve(grid, State((0, col), Direction.DOWN))
                for col in range(grid_size)
            ),
            # right, facing left
            *(
                self._solve(grid, State((row, grid_size - 1), Direction.LEFT))
                for row in range(grid_size)
            ),
            # bottom, facing up
            *(
                self._solve(grid, State((grid_size - 1, col), Direction.UP))
                for col in range(grid_size)
            ),
            # left, facing right
            *(
                self._solve(grid, State((row, 0), Direction.RIGHT))
                for row in range(grid_size)
            ),
        )
