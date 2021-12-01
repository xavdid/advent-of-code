# prompt: https://adventofcode.com/2020/day/15

from ...base import BaseSolution, InputTypes, slow


class Solution(BaseSolution):
    _year = 2020
    _number = 15
    input_type = InputTypes.INTSPLIT
    separator = ","

    def calculate_sequence(self, loops):
        # 1-index the turns now so we start our loop with
        # the index on the last input element, not after it
        mem = {value: index + 1 for index, value in enumerate(self.input)}
        last_num = self.input[-1]

        for turn in range(len(self.input), loops):
            to_speak = turn - mem[last_num] if last_num in mem else 0
            mem[last_num] = turn
            last_num = to_speak

        return last_num

    def part_1(self) -> int:
        return self.calculate_sequence(2020)

    @slow
    def part_2(self) -> int:
        return self.calculate_sequence(30_000_000)
