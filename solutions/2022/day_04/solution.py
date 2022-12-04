# prompt: https://adventofcode.com/2022/day/4

from typing import Callable, Set

from ...base import StrSplitSolution, answer


def pair_to_range(pair: str) -> Set[int]:
    start, stop = pair.split("-")
    return set(range(int(start), int(stop) + 1))


class Solution(StrSplitSolution):
    _year = 2022
    _day = 4

    def _solve(self, f: Callable[[Set[int], Set[int]], bool]) -> int:
        return sum(f(*map(pair_to_range, line.split(","))) for line in self.input)

    @answer(576)
    def part_1(self) -> int:
        return self._solve(lambda a, b: a <= b or b <= a)

    @answer(905)
    def part_2(self) -> int:
        return self._solve(lambda a, b: bool(a & b))
