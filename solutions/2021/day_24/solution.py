# prompt: https://adventofcode.com/2021/day/24


from dataclasses import dataclass
from typing import Iterable, List

from ...base import StrSplitSolution, answer


# https://stackoverflow.com/a/312464/1825390
def blocks(l: List[str]) -> Iterable[List[str]]:
    n = 18
    for i in range(0, len(l), n):
        yield l[i : i + n]


def get_int_from_line(line: str) -> int:
    return int(line.split(" ")[-1])


@dataclass
class Frame:
    # which place this frame represents in the final number
    digit: int
    # push or pop
    operation: int
    # the relevant variable for this operation
    var: int


PUSH_OP = 1


class Solution(StrSplitSolution):
    _year = 2021
    _day = 24

    def _solve(self, find_high: bool) -> int:
        stack: List[Frame] = []
        result: List[str] = [""] * 14

        for idx, block in enumerate(blocks(self.input)):
            op = get_int_from_line(block[4])

            var = get_int_from_line(block[15 if op == PUSH_OP else 5])

            curr = Frame(idx, op, var)

            if curr.operation == PUSH_OP:
                stack.append(curr)
                continue

            # the higher-power number
            prev = stack.pop()

            # the pair of numbers must differ by this much
            diff = prev.var + curr.var

            if find_high:
                if diff > 0:
                    result[prev.digit] = str(9 - diff)
                    result[curr.digit] = str(9)
                else:
                    result[prev.digit] = str(9)
                    result[curr.digit] = str(9 + diff)
            else:
                if diff > 0:
                    result[prev.digit] = str(1)
                    result[curr.digit] = str(1 + diff)
                else:
                    result[prev.digit] = str(1 - diff)
                    result[curr.digit] = str(1)

        assert all(result)
        assert len(result) == 14
        out = "".join(result)
        assert len(out) == 14

        return int(out)

    @answer(53999995829399)
    def part_1(self):
        return self._solve(True)

    @answer(11721151118175)
    def part_2(self) -> int:
        return self._solve(False)
