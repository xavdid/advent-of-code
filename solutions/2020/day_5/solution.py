# prompt: https://adventofcode.com/2020/day/5

from math import floor
from typing import Tuple

from ...base import BaseSolution, InputTypes


def get_midpoint(low: int, high: int) -> int:
    return floor((low + high) / 2)


def binary_search(instructions: int, top: int) -> int:
    low = 0
    high = top
    mid = floor((high + low) / 2)
    for c in instructions:
        if c in ("F", "L"):
            # bottom half
            high = mid
            mid = get_midpoint(low, high)
        else:
            # top half
            low = mid + 1
            mid = get_midpoint(low, high)

    return mid


def calulate_score(assignment: str) -> int:
    return (binary_search(assignment[:7], 127) * 8) + binary_search(assignment[7:], 7)


class Solution(BaseSolution):
    _year = 2020
    _number = 5
    input_type = InputTypes.STRSPLIT

    def solve(self) -> Tuple[int, int]:
        seat_ids = {calulate_score(assignment) for assignment in self.input}

        lowest = min(seat_ids)
        highest = max(seat_ids)

        full_range = set(range(lowest, highest + 1))

        return highest, (full_range - seat_ids).pop()
