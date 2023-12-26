# prompt: https://adventofcode.com/2023/day/18

from itertools import pairwise
from typing import Callable

from solutions.utils.graphs import GridPoint, add_points

from ...base import StrSplitSolution, answer

OFFSETS: dict[str, GridPoint] = {
    "R": (0, 1),
    "D": (1, 0),
    "L": (0, -1),
    "U": (-1, 0),
}
OFFSET_INDEXES = list(OFFSETS.values())


def num_points(outline: list[GridPoint], border_length: int) -> int:
    """
    the number of the points inside an outline plus the number of points in the outline
    """
    # shoelace - find the float area in a shape
    area = (
        sum(
            row1 * col2 - row2 * col1
            for (row1, col1), (row2, col2) in pairwise(outline)
        )
        / 2
    )
    # pick's theorem - find the number of points in a shape given its area
    return int(abs(area) - 0.5 * border_length + 1) + border_length


class Solution(StrSplitSolution):
    _year = 2023
    _day = 18

    def _solve(self, get_heading: Callable[[str], tuple[GridPoint, int]]):
        outline: list[GridPoint] = [(0, 0)]
        border_length = 0

        for line in self.input:
            offset, distance = get_heading(line)

            scaled_offset = (offset[0] * distance, offset[1] * distance)
            outline.append(add_points(scaled_offset, outline[-1]))
            border_length += distance

        return num_points(outline, border_length)

    @answer(70026)
    def part_1(self) -> int:
        def parse_line(line: str):
            direction, distance_str, _ = line.split()
            return OFFSETS[direction], int(distance_str)

        return self._solve(parse_line)

    @answer(68548301037382)
    def part_2(self) -> int:
        def parse_line(line: str):
            _, _, hex_str = line.split()
            offset = OFFSET_INDEXES[int(hex_str[-2])]
            distance = int(hex_str[2:-2], 16)
            return offset, distance

        return self._solve(parse_line)
