# prompt: https://adventofcode.com/2021/day/8

from typing import Dict, List

from ...base import StrSplitSolution, answer


def validate(i: List[str]):
    assert len(i) == 1
    return i[0]


class Solution(StrSplitSolution):
    _year = 2021
    _day = 8

    @answer(530)
    def part_1(self) -> int:
        UNIQUE_SIZES = {2, 3, 4, 7}
        total = 0

        for line in self.input:
            _, wires = line.split(" | ")
            total += sum([1 for x in wires.split() if len(x) in UNIQUE_SIZES])
        return total

    @answer(1051087)
    def part_2(self) -> int:
        total = 0
        for line in self.input:
            digits, number = line.split(" | ")
            result: Dict[int, str] = {}

            digits = digits.split()

            result[1] = validate([x for x in digits if len(x) == 2])
            result[4] = validate([x for x in digits if len(x) == 4])
            result[7] = validate([x for x in digits if len(x) == 3])
            result[8] = validate([x for x in digits if len(x) == 7])

            result[6] = validate(
                [x for x in digits if len(x) == 6 and not set(result[1]) < set(x)]
            )
            result[3] = validate(
                [x for x in digits if len(x) == 5 and set(result[1]) < set(x)]
            )

            found = set(result.values())
            digits = [x for x in digits if x not in found]

            result[9] = validate(
                [x for x in digits if len(x) == 6 and set(result[4]) < set(x)]
            )
            result[0] = validate([x for x in digits if len(x) == 6 and x != result[9]])

            # last 2!
            found = set(result.values())
            digits = [x for x in digits if x not in found]

            bottom_left = (set(result[8]) - set(result[9])).pop()
            result[2] = validate([x for x in digits if bottom_left in x])
            result[5] = validate([x for x in digits if x != result[2]])

            decoded = {frozenset(v): str(k) for k, v in result.items()}

            total += int("".join([decoded[frozenset(x)] for x in number.split()]))

        return total
