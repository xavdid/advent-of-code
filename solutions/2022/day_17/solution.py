# prompt: https://adventofcode.com/2022/day/17

from dataclasses import dataclass
from itertools import cycle
from typing import Literal, cast

from ...base import TextSolution, answer
from ...utils.graphs import GridPoint

Points = set[GridPoint]


def is_in_range(p: GridPoint) -> bool:
    return 0 <= p[0] < 7 and p[1] >= 0


def all_in_range(points: Points) -> bool:
    return all(map(is_in_range, points))


def print_grid(points: Points, max_y: int, min_y: int = -1):
    result = []
    for y in range(max_y + 2, min_y, -1):
        result.append(f'|{"".join("#" if (x,y) in points else "." for x in range(7))}|')
    if min_y == -1:
        result.append("+-------+")
    print("\n".join(result))


Direction = Literal["<", ">", "down"]

OFFSETS: dict[Direction, tuple[int, int]] = {"<": (-1, 0), ">": (1, 0), "down": (0, -1)}


@dataclass
class Block:
    points: Points

    def moved_points(self, direction: Direction) -> Points:
        o_x, o_y = OFFSETS[direction]
        return {(x + o_x, y + o_y) for x, y in self.points}

    @property
    def highest_point(self) -> int:
        return max(y for _, y in self.points)

    @property
    def name(self):
        return self.__class__.__name__


class Horiz(Block):
    def __init__(self, y: int):
        super().__init__({(x, y) for x in range(2, 6)})


class Plus(Block):
    def __init__(self, y: int):
        super().__init__({(3, y + 2), (2, y + 1), (3, y + 1), (4, y + 1), (3, y)})


class Angle(Block):
    def __init__(self, y: int):
        super().__init__({(2, y), (3, y), (4, y), (4, y + 1), (4, y + 2)})


class Vert(Block):
    def __init__(self, y: int):
        super().__init__({(2, y) for y in range(y, y + 4)})


class Square(Block):
    def __init__(self, y: int):
        super().__init__({(2, y), (3, y), (2, y + 1), (3, y + 1)})


class Solution(TextSolution):
    _year = 2022
    _day = 17

    def simulate_blocks(self, num_blocks: int) -> int:
        blocks = cycle([Horiz, Plus, Angle, Vert, Square])

        wind = cycle(enumerate(self.input))
        wind_index = 0

        settled_points: set[GridPoint] = set()

        settled_lines: dict[int, str] = {-1: "1111111"}  # floor
        height_to_add = 0
        max_y = -1  # below the floor

        # block_name, wind_index, top_row_value => block_num, max_y
        start_states: dict[tuple[str, int, str], tuple[int, int]] = {}

        def line_value(line: int) -> str:
            return "".join(str(int((x, line) in settled_points)) for x in range(7))

        block_number = 0
        while block_number < num_blocks:
            block = next(blocks)(max_y + 4)  # "3 above" means + 4

            state = (block.name, wind_index, settled_lines.get(max_y, "not found"))

            if (
                (previous_state := start_states.get(state))
                and block.name == "Horiz"
                and height_to_add == 0
            ):
                blocks_per_loop = block_number - previous_state[0]
                loops_to_skip = (num_blocks - block_number) // blocks_per_loop
                block_number += loops_to_skip * blocks_per_loop

                height_per_loop = max_y - previous_state[1]
                height_to_add = loops_to_skip * height_per_loop

            elif height_to_add == 0:
                # only track these before we've found a loop
                start_states[state] = (block_number, max_y)

            while True:
                # L/R
                wind_index, wind_direction = next(wind)
                new_points = block.moved_points(cast(Direction, wind_direction))
                if new_points.isdisjoint(settled_points) and all_in_range(new_points):
                    block.points = new_points

                # down
                new_points = block.moved_points("down")
                if new_points.isdisjoint(settled_points) and all_in_range(new_points):
                    block.points = new_points
                else:
                    break

            settled_points |= block.points
            max_y = max(max_y, block.highest_point)
            settled_lines[max_y] = line_value(max_y)

            block_number += 1

        return max_y + 1 + height_to_add

    @answer(3161)
    def part_1(self) -> int:
        return self.simulate_blocks(2022)

    @answer(1575931232076)
    def part_2(self) -> int:
        return self.simulate_blocks(1_000_000_000_000)
