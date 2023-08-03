# prompt: https://adventofcode.com/2022/day/25

from ...base import StrSplitSolution, answer

MULTIPLIERS = {"2": 2, "1": 1, "0": 0, "-": -1, "=": -2}


def from_snafu(s: str) -> int:
    return sum(5**idx * MULTIPLIERS[c] for idx, c in enumerate(reversed(s)))


def to_snafu(i: int) -> str:
    result = ""

    while i > 0:
        remainder = i % 5

        if remainder >= 3:
            result += {3: "=", 4: "-"}[remainder]
            i += 5 - remainder
        else:
            result += str(remainder)

        i //= 5

    return result[::-1]


class Solution(StrSplitSolution):
    _year = 2022
    _day = 25

    @answer("2=222-2---22=1=--1-2")
    def part_1(self) -> str:
        target = sum(from_snafu(line) for line in self.input)
        return to_snafu(target)
