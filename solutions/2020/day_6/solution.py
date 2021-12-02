# prompt: https://adventofcode.com/2020/day/6

from ...base import BaseSolution


class Solution(BaseSolution):
    _year = 2020
    _day = 6

    def part_1(self) -> int:
        groups = self.input.split("\n\n")
        total = 0
        for group in groups:
            all_chars_as_str = "".join(group.split("\n"))
            total += len(set(all_chars_as_str))
        return total

    def part_2(self) -> int:
        groups = self.input.split("\n\n")
        total = 0
        for group in groups:
            answers = [set(x) for x in group.split("\n")]
            total += len(answers[0].intersection(*answers[1:]))

        return total
