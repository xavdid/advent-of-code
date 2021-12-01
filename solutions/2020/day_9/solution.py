# prompt: https://adventofcode.com/2020/day/9

from itertools import combinations
from typing import Tuple

from ...base import BaseSolution, InputTypes

PREAMBLE_SIZE = 25


class Solution(BaseSolution):
    _year = 2020
    _number = 9
    input_type = InputTypes.INTSPLIT

    def solve(self) -> Tuple[int, int]:
        bad_num: int = None

        for i in range(PREAMBLE_SIZE, len(self.input)):
            sums = {
                sum(pair) for pair in combinations(self.input[i - PREAMBLE_SIZE : i], 2)
            }
            if self.input[i] not in sums:
                bad_num = self.input[i]

        for range_start in range(len(self.input)):
            # starting at the range_start index, keep adding
            # subsequent numbers until either we hit our number or surpass it
            running_sum = self.input[range_start]
            for range_end in range(range_start + 1, len(self.input)):
                running_sum += self.input[range_end]
                if running_sum == bad_num:
                    continuous_range = self.input[range_start : range_end + 1]
                    return bad_num, min(continuous_range) + max(continuous_range)
                if running_sum > bad_num:
                    break
