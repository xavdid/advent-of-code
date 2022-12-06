# prompt: https://adventofcode.com/2022/day/5


from itertools import zip_longest
from typing import Callable, Generator, Tuple

from ...base import StrSplitSolution, answer


class Solution(StrSplitSolution):
    _year = 2022
    _day = 5

    separator = "\n\n"

    def parse_stacks(self):
        lines = self.input[0].split("\n")
        misc_groups = zip_longest(*reversed(lines))
        result = [[]]
        for group in misc_groups:
            head = group[0] or ""
            if not head.strip().isdigit():
                continue

            result.append([c for c in group[1:] if c and c.strip()])

        return result

    def parse_instructions(self) -> Generator[Tuple[int, int, int], None, None]:
        for l in self.input[1].split("\n"):
            _, num, _, src, _, dst = l.split(" ")
            yield int(num), int(src), int(dst)

    def _solve(self, slicer: Callable[[int], slice]) -> str:
        stacks = self.parse_stacks()

        for num, src, dst in self.parse_instructions():
            stacks[dst] += stacks[src][slicer(num)]
            del stacks[src][-num:]

        return "".join(s[-1] for s in stacks[1:])

    @answer("VGBBJCRMN")
    def part_1(self) -> str:
        return self._solve(lambda num: slice(None, -num - 1, -1))

    @answer("LBBVJBRMH")
    def part_2(self) -> str:
        return self._solve(lambda num: slice(-num, None))
