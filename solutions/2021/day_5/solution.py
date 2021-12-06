# prompt: https://adventofcode.com/2021/day/5

from collections import Counter
from dataclasses import dataclass
from typing import List, Set, Tuple

from ...base import StrSplitSolution, answer


@dataclass(frozen=True, eq=True)
class Point:
    x: int
    y: int

    @staticmethod
    def from_input(input_: str) -> "Point":
        x, y = input_.split(",")
        return Point(int(x), int(y))


@dataclass
class Segment:
    start: Point
    stop: Point

    @property
    def is_flat(self) -> bool:
        """
        Exactly vertical or horizontal
        """
        return self.start.x == self.stop.x or self.start.y == self.stop.y

    @property
    def is_diagonal(self) -> bool:
        """
        Exactly a 45 degree angle
        """
        return abs(self.start.x - self.stop.x) == abs(self.start.y - self.stop.y)

    @property
    def points(self) -> List[Point]:
        x_min = min(self.start.x, self.stop.x)
        x_max = max(self.start.x, self.stop.x)
        x_vals = range(x_min, x_max + 1)

        y_min = min(self.start.y, self.stop.y)
        y_max = max(self.start.y, self.stop.y)
        y_vals = range(y_min, y_max + 1)

        if self.is_flat:
            if self.start.x == self.stop.x:
                return [Point(self.start.x, y) for y in y_vals]
            return [Point(x, self.start.y) for x in x_vals]

        if self.start.x > self.stop.x:
            x_vals = reversed(x_vals)

        if self.start.y > self.stop.y:
            y_vals = reversed(y_vals)

        return [Point(x, y) for x, y in zip(x_vals, y_vals)]


def num_repeated(c: Counter) -> int:
    return len([v for v in c.values() if v > 1])


class Solution(StrSplitSolution):
    _year = 2021
    _day = 5

    @answer((5145, 16518))
    def solve(self) -> Tuple[int, int]:
        part_1 = Counter()
        part_2 = Counter()

        for line in self.input:
            start, stop = line.split(" -> ")
            s = Segment(Point.from_input(start), Point.from_input(stop))
            if s.is_flat:
                part_1.update(s.points)
                part_2.update(s.points)
            if s.is_diagonal:
                part_2.update(s.points)

        return num_repeated(part_1), num_repeated(part_2)
