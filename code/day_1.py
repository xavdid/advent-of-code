# prompt: https://adventofcode.com/2017/day/1

from base import BaseSolution


class Solution(BaseSolution):
    def part_1(self):
        return self.solve(1)

    def part_2(self):
        return self.solve(len(self.input) / 2)

    def solve(self, jump):
        total = 0

        for i, val in enumerate(self.input):
            if val == self.input[(i + jump) % len(self.input)]:
                total += int(val)

        return total

