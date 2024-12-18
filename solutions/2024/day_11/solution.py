# prompt: https://adventofcode.com/2024/day/11

from collections import defaultdict
from itertools import chain

from ...base import StrSplitSolution, answer


def step_stone(s: str) -> list[str]:
    if s == "0":
        return ["1"]

    if (l := len(s)) % 2 == 0:
        cut_line = l // 2
        return [str(int(new_stone)) for new_stone in (s[:cut_line], s[cut_line:])]

    return [str(int(s) * 2024)]


class Solution(StrSplitSolution):
    _year = 2024
    _day = 11
    separator = " "

    @answer(239714)
    def part_1(self) -> int:
        stones = self.input

        for _ in range(25):
            stones = chain.from_iterable(map(step_stone, stones))

        return len(list(stones))

    @answer(284973560658514)
    def part_2(self) -> int:
        stones: dict[str, int] = {k: 1 for k in self.input}
        assert len(stones) == len(self.input)

        for _ in range(75):
            new_stones = defaultdict(int)
            for stone, num in stones.items():
                for new_stone in step_stone(stone):
                    new_stones[new_stone] += num

            stones = new_stones

        return sum(stones.values())
