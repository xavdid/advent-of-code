# prompt: https://adventofcode.com/2019/day/4

from ...base import BaseSolution


def is_valid_password(num: int):
    # could check length, but the whole range is valid
    last = -999
    has_double = False
    for i in map(int, str(num)):
        if i == last:
            has_double = True
        if i < last:
            return False
        last = i
    return has_double


def is_revised_valid_password(num: int):
    # same as above, but gropus of 3+ no longer count as the double
    last = -999
    has_double = False
    streak = 0

    for i in map(int, str(num)):
        if i == last:
            streak += 1
        else:
            if streak == 1:
                has_double = True
            streak = 0
        if i < last:
            return False
        last = i

    return has_double or streak == 1  # to catch numbers at the end


class Solution(BaseSolution):
    year = 2019
    number = 4

    def part_1(self):
        return self._solve(is_valid_password)

    def part_2(self):
        return self._solve(is_revised_valid_password)

    def _solve(self, func):
        parsed_input = self.input.split("-")
        bounds = range(int(parsed_input[0]), int(parsed_input[1]) + 1)
        return len([i for i in bounds if func(i)])
