# prompt: https://adventofcode.com/2022/day/20

from collections import deque
from typing import NamedTuple, Optional

from ...base import IntSplitSolution, answer


class Item(NamedTuple):
    id: int
    value: int


class Solution(IntSplitSolution):
    _year = 2022
    _day = 20

    def _solve(self, multiplier: int, num_mixes: int):
        items = [Item(idx, value * multiplier) for idx, value in enumerate(self.input)]
        num_items = len(items)

        d = deque(items)
        zero: Optional[Item] = None

        for _ in range(num_mixes):
            for item in items:
                if zero is None and item.value == 0:
                    zero = item

                d.rotate(-d.index(item))
                assert d[0] == item

                d.popleft()

                # -1 because we're down one item
                rotation = item.value % (num_items - 1)

                d.rotate(-rotation)
                d.appendleft(item)

        assert zero
        d.rotate(-d.index(zero))

        return sum(d[c * 1000 % num_items].value for c in [1, 2, 3])

    @answer(7228)
    def part_1(self) -> int:
        return self._solve(1, 1)

    @answer(4526232706281)
    def part_2(self) -> int:
        return self._solve(811589153, 10)
