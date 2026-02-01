# prompt: https://adventofcode.com/2025/day/3
# explanation: https://advent-of-code.xavd.id/writeups/2025/day/3/

from ...base import StrSplitSolution, answer


def _recursive_joltage(digits: list[int], length: int) -> list[int]:
    if length == 1:
        return [max(digits)]

    best_lead = max(digits[: -(length - 1)])
    lead_index = digits.index(best_lead)

    return [best_lead] + _recursive_joltage(digits[lead_index + 1 :], length - 1)


def highest_joltage(num: str, length: int) -> int:
    digits = _recursive_joltage([int(i) for i in num], length)
    return int("".join(map(str, digits)))


class Solution(StrSplitSolution):
    _year = 2025
    _day = 3

    def _solve(self, length: int) -> int:
        return sum(highest_joltage(line, length) for line in self.input)

    @answer(17332)
    def part_1(self) -> int:
        return self._solve(2)

    @answer(172516781546707)
    def part_2(self) -> int:
        return self._solve(12)
