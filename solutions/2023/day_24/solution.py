# prompt: https://adventofcode.com/2023/day/24

from dataclasses import dataclass
from functools import cached_property
from itertools import combinations

from ...base import StrSplitSolution, answer


def parse_3d_point(point: str) -> list[int]:
    return list(map(int, point.split(", ")))


@dataclass
class Hailstone:
    px: int
    py: int
    pz: int

    vx: int
    vy: int
    vz: int

    @staticmethod
    def parse(line: str) -> "Hailstone":
        position, velocity = line.split(" @ ")
        values = [*parse_3d_point(position), *parse_3d_point(velocity)]
        return Hailstone(*values)

    @cached_property
    def slope(self) -> float:
        return self.vy / self.vx

    @cached_property
    def y_intercept(self):
        """
        the height at which this line hits the y axis
        """
        return self.py - self.slope * self.px

    def is_point_in_past(self, x) -> bool:
        """
        depending which direction we're moving, we have to know if the intersection x
        point is in our future or past
        """
        if self.vx > 0:
            return self.px > x

        return self.px < x


class Solution(StrSplitSolution):
    _year = 2023
    _day = 24

    @answer(17867)
    def part_1(self) -> int:
        hailstones = [Hailstone.parse(line) for line in self.input]

        if self.use_test_data:
            BOUNDS_MIN = 7
            BOUNDS_MAX = 27
        else:
            BOUNDS_MIN = 200_000_000_000_000
            BOUNDS_MAX = 400_000_000_000_000

        total = 0
        for l, r in combinations(hailstones, 2):
            # if parallel, no intersection
            if l.slope == r.slope:
                continue

            x_intersection = (r.y_intercept - l.y_intercept) / (l.slope - r.slope)
            y_intersection = l.slope * x_intersection + l.y_intercept

            if l.is_point_in_past(x_intersection) or r.is_point_in_past(x_intersection):
                continue

            if (
                BOUNDS_MIN <= x_intersection <= BOUNDS_MAX
                and BOUNDS_MIN <= y_intersection <= BOUNDS_MAX
            ):
                total += 1

        return total

    # @answer(1234)
    def part_2(self) -> int:
        pass

    # @answer((1234, 4567))
    # def solve(self) -> tuple[int, int]:
    #     pass
