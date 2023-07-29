# prompt: https://adventofcode.com/2022/day/24

from dataclasses import dataclass, field
from heapq import heappop, heappush
from typing import Literal

from ...base import GridPoint, TextSolution, answer, neighbors

DIRECTIONS = Literal["<", ">", "v", "^"]
OFFSETS: dict[DIRECTIONS, GridPoint] = {
    "<": (0, -1),
    ">": (0, 1),
    "v": (1, 0),
    "^": (-1, 0),
}
Step = tuple[int, GridPoint]


@dataclass
class Blizzard:
    direction: DIRECTIONS
    position: GridPoint
    max_row: int = field(repr=False)
    max_col: int = field(repr=False)

    def move(self):
        offset_row, offset_col = OFFSETS[self.direction]

        self.position = (
            (self.position[0] + offset_row) % self.max_row,
            (self.position[1] + offset_col) % self.max_col,
        )


class Grid:
    # the occupied points at a moment in time
    states: dict[int, set[GridPoint]] = {}
    blizzards: list[Blizzard] = []

    top_left_point: GridPoint = 0, 0
    steps_taken = 0

    def __init__(self, raw_grid: str) -> None:
        rows = raw_grid.split("\n")
        self.max_rows = len(rows) - 2
        self.max_cols = len(rows[0]) - 2
        self.bottom_right_point: GridPoint = self.max_rows - 1, self.max_cols - 1

        for row, line in enumerate(rows[1:-1]):
            for col, c in enumerate(line[1:-1]):
                if c not in OFFSETS:
                    continue

                self.blizzards.append(
                    Blizzard(c, (row, col), self.max_rows, self.max_cols)
                )

        self.states[0] = {b.position for b in self.blizzards}

    def state_at(self, time: int) -> set[GridPoint]:
        while time not in self.states:
            self.steps_taken += 1
            for b in self.blizzards:
                b.move()
            self.states[self.steps_taken] = {b.position for b in self.blizzards}

        return self.states[time]

    def run(self, start_time: int, end_point: GridPoint) -> int:
        assert end_point in {self.top_left_point, self.bottom_right_point}

        start_point: GridPoint = (-1, -1)
        # time and expedition location
        queue: list[Step] = [(start_time, start_point)]
        visited: set[Step] = set()

        while queue:
            now = heappop(queue)
            if now in visited:
                continue
            visited.add(now)

            t, pos = now
            next_t = t + 1

            # if we're next to the exit, we can always move there
            if pos == end_point:
                return next_t

            assert (
                pos not in self.states[t]
            ), f"Invalid! Occupied tile {pos} at time {t} at the same time a storm did"

            next_state = self.state_at(next_t)

            # from the starting position, there are 2 options (neither of which could be in seen yet)
            if pos == start_point:
                # we can _always_ wait on the starting point
                heappush(queue, (next_t, start_point))

                # the point you can move to from the start varies based on where you're headed
                if (
                    start_neighbor := self.top_left_point
                    if end_point == self.bottom_right_point
                    else self.bottom_right_point
                ) not in next_state:
                    heappush(queue, (next_t, start_neighbor))
                continue

            # can maybe wait
            if pos not in next_state:
                heappush(queue, (next_t, pos))

            # check neighbors
            for potential_move in neighbors(
                pos,
                num_directions=4,
                ignore_negatives=True,
                max_x_size=self.max_rows - 1,
                max_y_size=self.max_cols - 1,
            ):
                if potential_move in next_state:
                    continue
                if (potential_state := (next_t, potential_move)) in visited:
                    continue

                heappush(queue, potential_state)

        raise ValueError("no solution found!")


class Solution(TextSolution):
    _year = 2022
    _day = 24

    @answer((242, 720))
    def solve(self) -> tuple[int, int]:
        g = Grid(self.input)

        end_of_first_crossing = g.run(0, g.bottom_right_point)
        end_of_return_trip = g.run(end_of_first_crossing, g.top_left_point)
        end_of_second_crossing = g.run(end_of_return_trip, g.bottom_right_point)

        return end_of_first_crossing, end_of_second_crossing
