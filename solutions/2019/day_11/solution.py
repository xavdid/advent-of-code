# prompt: https://adventofcode.com/2019/day/11

from dataclasses import dataclass
from enum import Enum, auto
from typing import Set

from ..intcode import STOP_REASON, IntcodeComputer, IntcodeSolution


class Direction(Enum):
    NORTH = auto()
    EAST = auto()
    SOUTH = auto()
    WEST = auto()


DIRECTION_ORDER = [Direction.NORTH, Direction.EAST, Direction.SOUTH, Direction.WEST]
CHANGE_SET = {
    Direction.NORTH: (0, 1),
    Direction.SOUTH: (0, -1),
    Direction.EAST: (1, 0),
    Direction.WEST: (-1, 0),
}


@dataclass(frozen=True)
class Point:
    x: int
    y: int


class Robot:
    def __init__(self, program, start_white=False):
        self.brain = IntcodeComputer(program)  # starts on black
        self.location = Point(0, 0)
        self.painted_panels: Set[Point] = set()
        self.white_panels: Set[Point] = set()
        if start_white:
            self.white_panels.add(self.location)
        self._dir_index = 0

    def run(self):
        while not self.step():
            pass
        return len(self.painted_panels)

    def step(self):
        self.brain.add_input(1 if self.location in self.white_panels else 0)
        halted = self.brain.run(num_outputs=2) == STOP_REASON.HALTED
        [paint_color, direction] = self.brain.output[-2:]

        if paint_color == 1:
            self.white_panels.add(self.location)
        else:
            self.white_panels.discard(self.location)
        self.painted_panels.add(self.location)
        self.rotate_and_move(direction)
        return halted

    def rotate_and_move(self, direction):
        self._rotate(direction)
        self._move()

    def print_panels(self):
        min_x = min(point.x for point in self.painted_panels)
        min_y = min(point.y for point in self.painted_panels)
        max_x = max(point.x for point in self.painted_panels)
        max_y = max(point.y for point in self.painted_panels)

        for y in range(max_y, min_y - 1, -1):
            for x in range(min_x, max_x + 1):
                if Point(x, y) in self.white_panels:
                    print("#", end="")
                else:
                    print(" ", end="")
            print()

    def _rotate(self, direction):
        """Rotate 90deg in either direction"""
        change = 1 if direction == 1 else -1
        self._dir_index = (self._dir_index + change) % 4

    def _move(self):
        """step 1 forward in the current direction"""
        direction = DIRECTION_ORDER[self._dir_index]
        [x, y] = CHANGE_SET[direction]
        self.location = Point(self.location.x + x, self.location.y + y)


class Solution(IntcodeSolution):
    _year = 2019
    _day = 11

    def part_1(self):
        robbie = Robot(self.input)
        return robbie.run()

    def part_2(self):
        print()
        robbie = Robot(self.input, start_white=True)
        robbie.run()
        robbie.print_panels()
        return "read letters above"
