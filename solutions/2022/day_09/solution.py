# prompt: https://adventofcode.com/2022/day/9

from dataclasses import dataclass, field
from typing import Set

from ...base import StrSplitSolution, answer
from ...utils.graphs import GridPoint


def get_offset(direction: str) -> GridPoint:
    if direction == "U":
        return 0, 1
    if direction == "R":
        return 1, 0
    if direction == "D":
        return 0, -1
    if direction == "L":
        return -1, 0

    raise ValueError("unrecognized direction")


@dataclass
class RopeEnd:
    x: int = 0
    y: int = 0
    locations: Set[GridPoint] = field(default_factory=lambda: {(0, 0)})

    @property
    def loc(self):
        return self.x, self.y

    def offset(self, other: "RopeEnd") -> GridPoint:
        return self.x - other.x, self.y - other.y

    def move(self, offset: GridPoint):
        self.x += offset[0]
        self.y += offset[1]
        self.locations.add(self.loc)


def squish_offset(i: int) -> int:
    if i > 0:
        return 1
    if i < 0:
        return -1
    return 0


def should_move(o: GridPoint) -> bool:
    return abs(o[0]) > 1 or abs(o[1]) > 1


class Solution(StrSplitSolution):
    _year = 2022
    _day = 9

    def simulate_rope(self, rope_size: int) -> int:
        rope = [RopeEnd() for i in range(rope_size)]

        for line in self.input:
            direction, distance_str = line.split()
            head_offset = get_offset(direction)

            for _ in range(int(distance_str)):
                rope[0].move(head_offset)
                for a, b in zip(rope, rope[1:]):
                    tail_offset = a.offset(b)
                    if should_move(tail_offset):
                        b.move(tuple(map(squish_offset, tail_offset)))

        return len(rope[-1].locations)

    @answer(5619)
    def part_1(self) -> int:
        return self.simulate_rope(2)

    @answer(2376)
    def part_2(self) -> int:
        return self.simulate_rope(10)
