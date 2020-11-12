# prompt: https://adventofcode.com/2019/day/10
# pylint: disable=invalid-name

from dataclasses import dataclass
from math import gcd

from ...base import BaseSolution, InputTypes


@dataclass(frozen=True)
class Point:
    x: int
    y: int

    def simple_angle(self, other):
        x = other.x - self.x
        y = other.y - self.y
        div = gcd(x, y)
        return (x // div, y // div)


class Solution(BaseSolution):
    year = 2019
    number = 10

    @property
    def input_type(self):
        return InputTypes.ARRAY

    def part_1(self):
        points = []

        for y, line in enumerate(self.input):
            for x, val in enumerate(line):
                if val == "#":
                    points.append(Point(x, y))

        results = []
        for point in points:
            found_angles = set()
            for other_point in points:
                if other_point == point:
                    continue

                angle = point.simple_angle(other_point)
                found_angles.add(angle)

            results.append(len(found_angles))
        return max(results)

    def part_2(self):
        pass
        # only visible astroids can be shot, that's my part 1 algo
        # need to get all visible ones, then sort by clockwise order
        # order is tough though, not sure how exactly to order them

        # some online cheating says atan2 is the function I'd need to get quadrants

        # here's the full order in the example
        # key: 1aA; X is start
        # .q....tuv24...x..
        # no...rs.13w67..9y
        # lm...p...5.8abcd.
        # ..k.....X...ezA..
        # ..j.i.....h....gf

    def solve(self):
        pass
