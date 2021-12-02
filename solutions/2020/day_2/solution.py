# prompt: https://adventofcode.com/2020/day/2

from typing import Tuple

from ...base import BaseSolution, InputTypes


def parse_policy(line: str) -> Tuple[int, int, str, str]:
    policy, password = line.split(": ")

    counts, char = policy.split(" ")
    min_count, max_count = map(int, counts.split("-"))

    return min_count, max_count, char, password


class Solution(BaseSolution):
    _year = 2020
    _day = 2
    input_type = InputTypes.STRSPLIT

    def part_1(self) -> int:
        num_valid = 0
        for line in self.input:
            min_count, max_count, char, password = parse_policy(line)

            if min_count <= password.count(char) <= max_count:
                num_valid += 1

        return num_valid

    def part_2(self) -> int:
        num_valid = 0
        for line in self.input:
            first_index, second_index, char, password = parse_policy(line)

            if (password[first_index - 1] == char) ^ (
                password[second_index - 1] == char
            ):
                num_valid += 1

        return num_valid
