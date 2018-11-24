# prompt: https://adventofcode.com/2017/day/2

import csv
import os
from itertools import permutations
from .base import BaseSolution, InputTypes


class Solution(BaseSolution):
    def input_type(self):
        return InputTypes.TSV

    def part_1(self):
        return self._solve(self.diff)

    def part_2(self):
        return self._solve(self.find_evenly_divisible_values)

    def _solve(self, f):
        return sum([f(a) for a in self.input])

    def diff(self, arr):
        return max(arr) - min(arr)

    def find_evenly_divisible_values(self, arr):
        pairs = permutations(arr, r=2)
        for pair in pairs:
            if max(pair) % min(pair) == 0:
                return max(pair) // min(pair)

