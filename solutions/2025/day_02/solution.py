# prompt: https://adventofcode.com/2025/day/2
# explanation: https://advent-of-code.xavd.id/writeups/2025/day/2/

import re
from itertools import chain
from typing import Callable

from ...base import StrSplitSolution, answer


def is_valid(i: int) -> bool:
    s = str(i)
    str_len = len(s)
    # odd-length strings can't have 2 repeated halves
    if str_len % 2 == 1:
        return True

    midpoint = str_len // 2

    return s[:midpoint] != s[midpoint:]


def is_valid_repeated(i: int) -> bool:
    s = str(i)
    str_len = len(s)

    # 1-length nums can't have repeated digits
    if str_len == 1:
        return True

    # a single number repeated is invalid
    if len(set(s)) == 1:
        return False

    midpoint = str_len // 2
    for substr_len in range(2, midpoint + 1):
        num_occurances = s.count(s[:substr_len])
        if num_occurances * substr_len == str_len:
            return False

    return True


def is_valid_repeated_regex(i: int) -> bool:
    return not re.match(r"^(\d+)\1+$", str(i))


def parse_range(s: str) -> range:
    l, r = s.split("-")
    return range(int(l), int(r) + 1)  # inclusive


class Solution(StrSplitSolution):
    _year = 2025
    _day = 2
    separator = ","

    def _solve(self, validity_func: Callable[[int], bool]) -> int:
        return sum(
            i
            for i in chain.from_iterable(map(parse_range, self.input))
            if not validity_func(i)
        )

    @answer(17077011375)
    def part_1(self) -> int:
        return self._solve(is_valid)

    @answer(36037497037)
    def part_2(self) -> int:
        return self._solve(is_valid_repeated)
