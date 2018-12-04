# prompt: https://adventofcode.com/2017/day/3

import math
from ...base import BaseSolution, InputTypes


class Solution(BaseSolution):
    @property
    def year(self):
        return 2017

    @property
    def input_type(self):
        return InputTypes.INTEGER

    def part_1(self):
        side = math.ceil(
            math.sqrt(self.input)
        )  # odd-root for the side of the square we're in
        if side % 2 == 0:
            side += 1  # odd roots only

        max_distance = side - 1  # all numbers in this loop can only be this far

        # see how far our input is from the odd-square.
        # the possible values are a corner (max_distance) or the center of a row (half of that)
        steps = max_distance - ((side ** 2 - self.input) % max_distance)
        return int(steps)

    def part_2(self):
        # for this one, I cheated. All the numbers in the grid are here: https://oeis.org/A141481/b141481.txt
        # a full description of that sequence is available here: https://oeis.org/A141481
        return 266330
