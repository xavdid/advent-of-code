# prompt: https://adventofcode.com/2023/day/1

from ...base import StrSplitSolution, answer

NUMBERS = {
    "one": "1",
    "two": "2",
    "three": "3",
    "four": "4",
    "five": "5",
    "six": "6",
    "seven": "7",
    "eight": "8",
    "nine": "9",
}


def calculate_calibration(s: str, replace_nums=False) -> int:
    if replace_nums:
        for num, digit in NUMBERS.items():
            # don't remove the word, since some words are used twice
            s = s.replace(num, f"{num[0]}{digit}{num[-1]}")

    digits = [c for c in s if c.isdigit()]
    assert digits, "empty array!"

    return int(digits[0] + digits[-1])


class Solution(StrSplitSolution):
    _year = 2023
    _day = 1

    @answer(54953)
    def part_1(self) -> int:
        return sum(calculate_calibration(line) for line in self.input)

    @answer(53868)
    def part_2(self) -> int:
        return sum(
            calculate_calibration(line, replace_nums=True) for line in self.input
        )
