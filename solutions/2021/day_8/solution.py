# prompt: https://adventofcode.com/2021/day/8

from ...base import StrSplitSolution, answer

UNIQUE_SIZES = {2, 3, 4, 7}


class Solution(StrSplitSolution):
    _year = 2021
    _day = 8

    # @answer(530)
    def part_1(self) -> int:
        total = 0
        for line in self.input:
            _, wires = line.split(" | ")
            total += sum([1 for x in wires.split() if len(x) in UNIQUE_SIZES])
        return total

    # @answer(1234)
    def part_2(self) -> int:
        pass

    # answer((1234, 4567))
    # def solve(self) -> Tuple[int, int]:
    #     pass
