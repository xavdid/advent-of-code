# prompt: https://adventofcode.com/2023/day/24

from dataclasses import dataclass
from functools import cached_property
from itertools import combinations

from ...base import StrSplitSolution, answer


def parse_3d_point(point: str) -> list[int]:
    return list(map(int, point.split(", ")))


def possible_velocities(hailstone_v: int, distance: int) -> set[int]:
    return {
        v
        for v in range(-1000, 1000)
        if v != hailstone_v and distance % (v - hailstone_v) == 0
    }


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

    def velocity(self, dim: str) -> int:
        return getattr(self, f"v{dim}")

    def position(self, dim: str) -> int:
        return getattr(self, f"p{dim}")

    def slower_hailstone(self, rvx: int, rvy: int) -> "Hailstone":
        """
        given the 2D velocity of a rock, slow this hailstone down by that much
        """
        return Hailstone(
            self.px, self.py, self.pz, self.vx - rvx, self.vy - rvy, self.vz
        )

    def intersection_with(self, other: "Hailstone") -> tuple[float, float]:
        x_intersection = (other.y_intercept - self.y_intercept) / (
            self.slope - other.slope
        )
        y_intersection = self.slope * x_intersection + self.y_intercept

        return x_intersection, y_intersection


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

            x_intersection, y_intersection = l.intersection_with(r)

            if l.is_point_in_past(x_intersection) or r.is_point_in_past(x_intersection):
                continue

            if (
                BOUNDS_MIN <= x_intersection <= BOUNDS_MAX
                and BOUNDS_MIN <= y_intersection <= BOUNDS_MAX
            ):
                total += 1

        return total

    @answer(557743507346379)
    def part_2(self) -> int:
        """
        NOTE: adapted from https://www.reddit.com/r/adventofcode/comments/18pnycy/2023_day_24_solutions/keqf8uq/
        """
        hailstones = [Hailstone.parse(line) for line in self.input]

        rock_velocities = []
        for dim in "xyz":
            all_possibilities = [
                possible_velocities(l.velocity(dim), r.position(dim) - l.position(dim))
                for l, r in combinations(hailstones, 2)
                if l.velocity(dim) == r.velocity(dim)
            ]

            common_possibilities = all_possibilities[0].intersection(*all_possibilities)
            assert len(common_possibilities) == 1

            rock_velocities.append(common_possibilities.pop())

        rvx, rvy, rvz = rock_velocities

        a, b, *_ = hailstones
        # store un-slowed because we need it later
        avx = a.vx

        a = a.slower_hailstone(rvx, rvy)
        b = b.slower_hailstone(rvx, rvy)

        rpx, rpy = a.intersection_with(b)

        time = (rpx - a.px) / (avx - rvx)
        rpz = a.pz + (a.vz - rvz) * time

        return int(rpx + rpy + rpz)
