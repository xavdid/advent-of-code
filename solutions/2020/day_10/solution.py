# prompt: https://adventofcode.com/2020/day/10

from collections import defaultdict
from typing import List

from ...base import BaseSolution, InputTypes

# from typing import Tuple


class Solution(BaseSolution):
    _year = 2020
    _day = 10
    input_type = InputTypes.INTSPLIT

    def part_1(self) -> int:
        sorted_input: List[int] = sorted(self.input)
        adapters = [0, *sorted_input, sorted_input[-1] + 3]

        differences = defaultdict(int)
        for index, val in enumerate(adapters[:-1]):
            diff = adapters[index + 1] - val
            differences[diff] += 1

        return differences[1] * differences[3]

    def part_2(self) -> int:
        sorted_input: List[int] = sorted(self.input)
        max_value = sorted_input[-1] + 3
        adapters = [*sorted_input, max_value]
        num_paths = defaultdict(int, {0: 1})

        for adapter in adapters:
            num_paths[adapter] = (
                num_paths[adapter - 1] + num_paths[adapter - 2] + num_paths[adapter - 3]
            )

        return num_paths[max_value]
