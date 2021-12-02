# prompt: https://adventofcode.com/2020/day/3

from math import prod
from typing import Tuple

from ...base import BaseSolution, InputTypes


class Solution(BaseSolution):
    _year = 2020
    _day = 3
    input_type = InputTypes.STRSPLIT

    def count_trees(self, right: int, down: int) -> int:
        width = len(self.input[0])
        trees = 0

        for index, line in enumerate(self.input):
            if down > 1 and index % down != 0:
                continue

            if line[(index // down * right) % width] == "#":
                trees += 1

        return trees

    def solve(self) -> Tuple[int, int]:
        slopes = [(1, 1), (3, 1), (5, 1), (7, 1), (1, 2)]

        collisions = [self.count_trees(*slope) for slope in slopes]

        return collisions[1], prod(collisions)
