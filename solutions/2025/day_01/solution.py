# prompt: https://adventofcode.com/2025/day/1
# explanation: https://advent-of-code.xavd.id/writeups/2025/day/1/


from solutions.utils.transformations import ilen

from ...base import StrSplitSolution, answer


class Solution(StrSplitSolution):
    _year = 2025
    _day = 1

    @answer(1147)
    def part_1(self) -> int:
        current = 50
        num_zeroes = 0

        for line in self.input:
            direction, *raw_distance = line
            distance = int("".join(raw_distance))
            if direction == "L":
                distance *= -1

            current = (current + distance) % 100

            if current == 0:
                num_zeroes += 1

        return num_zeroes

    @answer(6789)
    def part_2(self) -> int:
        current = 50
        num_zeroes = 0

        for line in self.input:
            direction, *raw_distance = line
            distance = int("".join(raw_distance))

            step = -1 if direction == "L" else 1
            distance *= step

            num_zeroes += ilen(
                i for i in range(current, current + distance, step) if i % 100 == 0
            )

            current = (current + distance) % 100

        return num_zeroes
