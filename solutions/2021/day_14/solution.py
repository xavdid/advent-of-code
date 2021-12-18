# prompt: https://adventofcode.com/2021/day/14

from collections import Counter
from typing import Dict, Tuple

from ...base import StrSplitSolution, answer


class Solution(StrSplitSolution):
    _year = 2021
    _day = 14

    def _solve(self, steps: int) -> int:
        formula: Dict[Tuple, str] = {}
        for line in self.input[2:]:
            inp, out = line.split(" -> ")
            formula[tuple(inp)] = out

        chain = Counter(zip(self.input[0], self.input[0][1:]))
        counts = Counter(self.input[0])

        for _ in range(steps):
            # list() so we can modify chain as we go
            for (l, r), num in list(chain.items()):
                if not num:
                    continue

                chain[(l, r)] -= num
                out = formula[(l, r)]
                counts[out] += num

                chain[(l, out)] += num
                chain[(out, r)] += num

        return max(counts.values()) - min(counts.values())

    @answer((2657, 2911561572630))
    def solve(self) -> Tuple[int, int]:
        return self._solve(10), self._solve(40)
