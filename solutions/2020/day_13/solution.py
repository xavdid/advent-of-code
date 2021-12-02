# prompt: https://adventofcode.com/2020/day/13

from itertools import count
from math import ceil

from ...base import BaseSolution, InputTypes

# from typing import Tuple


class Solution(BaseSolution):
    _year = 2020
    _day = 13
    input_type = InputTypes.STRSPLIT

    def part_1(self) -> int:
        min_leave_time = int(self.input[0])
        bus_ids = [int(x) for x in self.input[1].split(",") if x != "x"]
        departure_time, best_bus = sorted(
            [(ceil(min_leave_time / bus_id) * bus_id, bus_id) for bus_id in bus_ids]
        )[0]

        return (departure_time - min_leave_time) * best_bus

    def part_2(self) -> int:
        buses = [
            (offset, int(bus_id))
            for offset, bus_id in enumerate(self.input[1].split(","))
            if bus_id != "x"
        ]

        # https://www.reddit.com/r/adventofcode/comments/kc4njx/2020_day_13_solutions/gfsc2gg/

        step = 1
        timestamp = 0
        for offset, bus_id in buses:
            timestamp = next(
                ts for ts in count(timestamp, step) if (ts + offset) % bus_id == 0
            )
            step *= bus_id
        return timestamp
