# prompt: https://adventofcode.com/2024/day/14

from collections import Counter, defaultdict
from dataclasses import dataclass
from itertools import product
from math import prod
from operator import gt, lt
from re import findall

from ...base import StrSplitSolution, answer
from ...utils.transformations import parse_ints


@dataclass
class Robot:
    num_cols: int
    num_rows: int
    col: int
    row: int
    v_col: int
    v_row: int

    @staticmethod
    def from_line(line: str, num_cols: int, num_rows: int) -> "Robot":
        # unknown-length items go last to type checker doesn't complain
        return Robot(num_cols, num_rows, *parse_ints(findall(r"-?\d+", line)))

    def step(self, distance=1) -> "Robot":
        self.row = (self.row + self.v_row * distance) % self.num_rows
        self.col = (self.col + self.v_col * distance) % self.num_cols
        return self

    @property
    def quadrant(self) -> int:
        row_boundary = self.num_rows // 2
        col_boundary = self.num_cols // 2

        for quadrant, (row_op, col_op) in enumerate(product([lt, gt], repeat=2)):
            if row_op(self.row, row_boundary) and col_op(self.col, col_boundary):
                return quadrant

        return -1

    @property
    def position(self) -> tuple[int, int]:
        return self.row, self.col


class Solution(StrSplitSolution):
    _year = 2024
    _day = 14

    def _get_boundaries(self) -> tuple[int, int]:
        if self.use_test_data:
            num_cols = 11
            num_rows = 7
        else:
            num_cols = 101
            num_rows = 103

        return num_rows, num_cols

    @answer(222901875)
    def part_1(self) -> int:
        num_rows, num_cols = self._get_boundaries()

        quadrants = defaultdict(int)
        for line in self.input:
            r = Robot.from_line(line, num_cols, num_rows)
            r.step(100)
            quadrants[r.quadrant] += 1

        return prod(quadrants[i] for i in range(4))

    @answer(6243)
    def part_2(self) -> int:
        num_rows, num_cols = self._get_boundaries()

        # find the "safest" page
        robots = [Robot.from_line(line, num_cols, num_rows) for line in self.input]
        pages: list[tuple[int, int]] = []
        for page_num in range(1, 100):
            quadrants = defaultdict(int)
            for r in robots:
                r.step()
                quadrants[r.quadrant] += 1

            score = prod(quadrants[q] for q in range(4))
            pages.append((score, page_num))

        _, START = sorted(pages)[0]

        # re-parse our robots to start fresh
        robots = [
            Robot.from_line(line, num_cols, num_rows).step(START) for line in self.input
        ]
        num_robots = len(robots)

        for i in range(1, 100):
            for r in robots:
                r.step(num_cols)

            locations = [r.position for r in robots]

            if len(set(locations)) == num_robots:
                grid = Counter(locations)
                self.debug(
                    "\n".join(
                        "".join(str(grid.get((r, c), ".")) for c in range(num_cols))
                        for r in range(num_rows)
                    )
                )
                self.debug()
                return START + num_cols * i

        raise ValueError("unable to find solution")
