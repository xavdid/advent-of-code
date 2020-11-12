# prompt: https://adventofcode.com/2017/day/1

from ...base import BaseSolution, slow


class Solution(BaseSolution):
    year = 2017
    number = 1

    def part_1(self):
        return self._solve(1)

    def part_2(self):
        return self._solve(len(self.input) // 2)

    def _solve(self, jump):
        total = 0

        for i, val in enumerate(self.input):
            if val == self.input[(i + jump) % len(self.input)]:
                total += int(val)

        return total

