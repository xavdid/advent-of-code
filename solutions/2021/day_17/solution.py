# prompt: https://adventofcode.com/2021/day/17

from dataclasses import dataclass
from re import findall
from typing import Tuple, cast

from ...base import TextSolution, answer

Range = Tuple[int, int]


@dataclass
class Probe:
    vel_x: int
    vel_y: int
    targ_x: Range
    targ_y: Range

    pos_x = 0
    pos_y = 0

    def step(self) -> None:
        self.pos_x += self.vel_x
        self.pos_y += self.vel_y

        if self.vel_x < 0:
            self.vel_x += 1
        if self.vel_x > 0:
            self.vel_x -= 1

        self.vel_y -= 1

    def is_in_target(self) -> bool:
        return (self.targ_x[0] <= self.pos_x <= self.targ_x[1]) and (
            self.targ_y[0] <= self.pos_y <= self.targ_y[1]
        )

    def fly(self) -> bool:
        """
        returns true if probe hit the target, false otherwise
        """

        while self.pos_x <= self.targ_x[1] and self.pos_y >= self.targ_y[0]:
            self.step()
            if self.is_in_target():
                return True

        return False


class Solution(TextSolution):
    _year = 2021
    _day = 17

    @answer((7381, 3019))
    def solve(self) -> Tuple[int, int]:
        ranges = [
            cast(Range, tuple(map(int, x)))
            for x in findall(r"(-?\d+)\.\.(-?\d+)", self.input)
        ]
        assert len(ranges) == 2, "Found too many ranges from input"

        y1 = ranges[1][0]
        # math magic based on physics
        max_y = y1 * (y1 + 1) // 2

        total = 0
        for x in range(int((ranges[0][0] * 2) ** 0.5), ranges[0][1] + 1):
            for y in range(y1, -y1):
                p = Probe(x, y, *ranges)
                if p.fly():
                    total += 1

        return max_y, total
