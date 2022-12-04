# prompt: https://adventofcode.com/2022/day/3

from string import ascii_letters

from ...base import StrSplitSolution, answer


def priority(letter: str) -> int:
    return ascii_letters.index(letter) + 1


def overlap_value(rucksack: str) -> int:
    mid_point = len(rucksack) // 2
    shared = set(rucksack[:mid_point]) & set(rucksack[mid_point:])
    return priority(shared.pop())


class Solution(StrSplitSolution):
    _year = 2022
    _day = 3

    @answer(8153)
    def part_1(self) -> int:
        return sum(overlap_value(rucksack) for rucksack in self.input)

    def groups(self):
        """Yield successive groups of 3 from input"""
        n = 3
        for i in range(0, len(self.input), n):
            yield self.input[i : i + n]

    @answer(2342)
    def part_2(self) -> int:
        return sum(
            priority((set(a) & set(b) & set(c)).pop()) for a, b, c in self.groups()
        )
