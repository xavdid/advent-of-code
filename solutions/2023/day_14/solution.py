# prompt: https://adventofcode.com/2023/day/14

from typing import Callable, cast

from solutions.utils.graphs import GridPoint, parse_grid

from ...base import StrSplitSolution, answer

Points = set[GridPoint]
RangeGen = Callable[[int], range]


def _roll(
    rocks: Points,
    walls: Points,
    reverse_sort: bool,
    range_builder: RangeGen,
    index_to_replace: int,
):
    for rock in sorted(rocks, reverse=reverse_sort):
        new_rock = None

        for potential_new_value in range_builder(rock[index_to_replace]):
            _new_rock = list(rock)
            _new_rock[index_to_replace] = potential_new_value
            potential_new_rock = tuple(_new_rock)

            if potential_new_rock in walls or potential_new_rock in rocks:
                break
            new_rock = potential_new_rock

        if new_rock is not None:
            rocks.remove(rock)
            rocks.add(cast(GridPoint, new_rock))


def roll_up(rocks: Points, walls: Points) -> None:
    _roll(
        rocks,
        walls,
        reverse_sort=False,
        range_builder=lambda row: range(row - 1, -1, -1),
        index_to_replace=0,
    )


def roll_down(rocks: Points, walls: Points, grid_size: int) -> None:
    _roll(
        rocks,
        walls,
        reverse_sort=True,
        range_builder=lambda row: range(row + 1, grid_size),
        index_to_replace=0,
    )


def roll_left(rocks: Points, walls: Points) -> None:
    _roll(
        rocks,
        walls,
        reverse_sort=False,
        range_builder=lambda col: range(col - 1, -1, -1),
        index_to_replace=1,
    )


def roll_right(rocks: Points, walls: Points, grid_size: int) -> None:
    _roll(
        rocks,
        walls,
        reverse_sort=True,
        range_builder=lambda col: range(col + 1, grid_size),
        index_to_replace=1,
    )


class Solution(StrSplitSolution):
    _year = 2023
    _day = 14

    @answer(110565)
    def part_1(self) -> int:
        rocks = set(parse_grid(self.input, ignore_chars=".#"))
        walls = set(parse_grid(self.input, ignore_chars=".O"))
        grid_height = len(self.input)

        roll_up(rocks, walls)

        return sum(grid_height - row for row, _ in rocks)

    @answer(89845)
    def part_2(self) -> int:
        rocks = set(parse_grid(self.input, ignore_chars=".#"))
        walls = set(parse_grid(self.input, ignore_chars=".O"))
        grid_size = len(self.input)
        NUM_CYCLES = 1_000_000_000

        states: dict[frozenset[GridPoint], int] = {}

        i = 0
        while i < NUM_CYCLES:
            roll_up(rocks, walls)
            roll_left(rocks, walls)
            roll_down(rocks, walls, grid_size)
            roll_right(rocks, walls, grid_size)

            state = frozenset(rocks)

            if state in states and i < 500:
                distance_to_goal = NUM_CYCLES - i
                loop_length = i - states[state]
                i = NUM_CYCLES - distance_to_goal % loop_length

            states[state] = i
            i += 1

        return sum(grid_size - row for row, _ in rocks)
