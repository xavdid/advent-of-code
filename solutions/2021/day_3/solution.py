# prompt: https://adventofcode.com/2021/day/3

from collections import Counter
from typing import Literal, Union

from ...base import StrSplitSolution, answer

one_or_zero = Union[Literal["0"], Literal["1"]]


class Solution(StrSplitSolution):
    _year = 2021
    _day = 3

    @answer(3958484)
    def part_1(self) -> int:
        gamma = "".join(
            [
                Counter(place_values).most_common(1)[0][0]
                for place_values in zip(*self.input)
            ]
        )
        epsilon = "".join(["0" if c == "1" else "1" for c in gamma])
        return int(gamma, 2) * int(epsilon, 2)

    @answer(1613181)
    def part_2(self) -> int:
        o2 = self.filter_list("1", "0", "1")
        co2 = self.filter_list("0", "1", "0")
        return int(o2, 2) * int(co2, 2)

    def filter_list(
        self,
        val_if_1_higher: one_or_zero,
        val_if_0_higher: one_or_zero,
        val_if_tied: one_or_zero,
    ) -> str:
        values = self.input
        result = ""

        while len(values) > 1:
            place_to_check = len(result)
            counts = Counter([i[place_to_check] for i in values])
            if counts["1"] > counts["0"]:
                result += val_if_1_higher
            elif counts["0"] > counts["1"]:
                result += val_if_0_higher
            else:
                result += val_if_tied

            values = [n for n in values if n.startswith(result)]

        return values[0]
