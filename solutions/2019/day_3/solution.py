# prompt: https://adventofcode.com/2019/day/3
# pylint: disable=invalid-name

from dataclasses import dataclass
from typing import Set, Union

from ...base import BaseSolution, InputTypes


@dataclass(frozen=True)
class Point:
    x: int
    y: int

    def distance_to_origin(self):
        return abs(self.x) + abs(self.y)


def points_between(x: Union[int, range], y: Union[int, range]):
    if isinstance(x, range):
        return [Point(i, y) for i in x]

    return [Point(x, i) for i in y]


def get_points_for_wire(points: str):
    x = 0
    y = 0
    res = [Point(0, 0)]  # array so it's easier to debug

    moves = points.split(",")
    for move in moves:
        direction, distance = [move[0], int(move[1:])]
        if direction == "R":
            res += points_between(range(x + 1, x + distance + 1), y)
            x += distance
        elif direction == "L":
            res += points_between(range(x - 1, x - distance - 1, -1), y)
            x -= distance
        elif direction == "U":
            res += points_between(x, range(y + 1, y + distance + 1))
            y += distance
        elif direction == "D":
            res += points_between(x, range(y - 1, y - distance - 1, -1))
            y -= distance
        else:
            raise ValueError("Unknown direction")
    return res


class Solution(BaseSolution):
    year = 2019
    number = 3

    @property
    def input_type(self):
        return InputTypes.ARRAY

    def solve(self):
        wire_a = get_points_for_wire(self.input[0])
        wire_b = get_points_for_wire(self.input[1])

        intersections: Set[Point] = set(wire_a) & set(wire_b)
        intersections.discard(Point(0, 0))

        distances_to_origin = []
        latencies = []

        for p in intersections:
            # part 1
            distances_to_origin.append(p.distance_to_origin())

            # part 2
            latencies.append(wire_a.index(p) + wire_b.index(p))

        return (min(distances_to_origin), min(latencies))
