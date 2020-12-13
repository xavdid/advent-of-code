# prompt: https://adventofcode.com/2020/day/13

from math import ceil

from ...base import BaseSolution, InputTypes

# from typing import Tuple


class Solution(BaseSolution):
    year = 2020
    number = 13
    input_type = InputTypes.STRSPLIT

    def part_1(self) -> int:
        min_leave_time = int(self.input[0])
        bus_ids = [int(x) for x in self.input[1].split(",") if x != "x"]
        departure_time, best_bus = sorted(
            [(ceil(min_leave_time / bus_id) * bus_id, bus_id) for bus_id in bus_ids]
        )[0]

        return (departure_time - min_leave_time) * best_bus

    def part_2(self) -> int:
        pass

    # def solve(self) -> Tuple[int, int]:
    #     pass
