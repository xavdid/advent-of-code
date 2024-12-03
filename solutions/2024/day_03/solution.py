# prompt: https://adventofcode.com/2024/day/3

import re

from ...base import TextSolution, answer


class Solution(TextSolution):
    _year = 2024
    _day = 3

    @answer(173785482)
    def part_1(self) -> int:
        return sum(
            int(l) * int(r)
            for l, r in re.findall(r"mul\((\d{1,3}),(\d{1,3})\)", self.input)
        )

    @answer(83158140)
    def part_2(self) -> int:
        instructions = re.finditer(
            r"mul\((\d{1,3}),(\d{1,3})\)|do\(\)|don't\(\)", self.input
        )

        total = 0
        active = True
        for i in instructions:
            command, l, r = i.group(0, 1, 2)
            if command == "do()":
                active = True
            elif command == "don't()":
                active = False
            elif active:
                total += int(l) * int(r)
            else:
                # we hit mul but are inactive; skip!
                pass

        return total
