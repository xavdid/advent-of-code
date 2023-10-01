# prompt: https://adventofcode.com/2017/day/2

import csv
from itertools import permutations

from ...base import StrSplitSolution


class Solution(StrSplitSolution):
    _year = 2017
    _day = 2

    def part_1(self):
        return self._solve(self.diff)

    def part_2(self):
        return self._solve(self.find_evenly_divisible_values)

    def _parse_tsv(self):
        reader = csv.reader(self.input, delimiter="\t")
        return [[int(i) for i in row] for row in reader]

    def _solve(self, f):
        return sum([f(a) for a in self._parse_tsv()])

    def diff(self, arr):
        return max(arr) - min(arr)

    def find_evenly_divisible_values(self, arr):
        pairs = permutations(arr, r=2)
        for pair in pairs:
            if max(pair) % min(pair) == 0:
                return max(pair) // min(pair)
