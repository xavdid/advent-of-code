# prompt: https://adventofcode.com/2020/day/25

from itertools import count

from ...base import BaseSolution, InputTypes

DIVISOR = 20201227


class Solution(BaseSolution):
    year = 2020
    number = 25
    input_type = InputTypes.INTSPLIT

    def part_1(self) -> int:
        card_public_key, door_public_key = self.input

        val = 1
        card_loop_size = None  # to help pylance
        for card_loop_size in count(start=1):
            val = (val * 7) % DIVISOR
            if val == card_public_key:
                break

        answer = pow(door_public_key, card_loop_size, DIVISOR)

        assert answer == 12285001
        return answer

    def part_2(self) -> int:
        pass
