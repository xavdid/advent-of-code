# prompt: https://adventofcode.com/2022/day/15

from dataclasses import InitVar, dataclass
from operator import itemgetter
from re import findall
from typing import Iterable

from ...base import GridPoint, StrSplitSolution, answer, slow

TUNING_MULTIPLIER = 4_000_000


@dataclass
class Sensor:
    x: int
    y: int
    beacon: InitVar[GridPoint]

    def __post_init__(self, beacon):
        self.reach = self.distance_to(beacon)

    def distance_to(self, point: GridPoint) -> int:
        return abs(self.x - point[0]) + abs(self.y - point[1])

    def can_reach(self, point: GridPoint) -> bool:
        return self.distance_to(point) <= self.reach

    def range_on_row(self, target_row: int, clamp_at: int) -> range | None:
        if not self.can_reach((self.x, target_row)):
            return None

        num_on_row = self.reach - abs(self.y - target_row)

        res = range(self.x - num_on_row, self.x + num_on_row)

        if clamp_at:
            return range(max(res.start, 0), min(res.stop, clamp_at))
        return res

    def enlarged_border_points(self, clamp_at: int) -> Iterable[GridPoint]:
        def in_range(x_, y_) -> bool:
            return 0 <= x_ <= clamp_at and 0 <= y_ <= clamp_at

        # start at the top of the diamond
        x = self.x
        y = self.y - self.reach - 1

        # go down and right
        change_x = 1
        change_y = 1
        while y < self.y:
            if in_range(x, y):
                yield x, y
            x += change_x
            y += change_y

        # go down and left
        change_x = -1
        while x > self.x:
            if in_range(x, y):
                yield x, y
            x += change_x
            y += change_y

        # go up and left
        change_y = -1
        while y > self.y:
            if in_range(x, y):
                yield x, y
            x += change_x
            y += change_y

        # go down and left
        change_x = 1
        while x < self.x:
            if in_range(x, y):
                yield x, y
            x += change_x
            y += change_y


class Solution(StrSplitSolution):
    _year = 2022
    _day = 15

    def parse_sensors(self) -> list[Sensor]:
        sensors: list[Sensor] = []

        for numbers in (
            tuple(map(int, findall(r"[\d-]+", line))) for line in self.input
        ):
            sensors.append(Sensor(numbers[0], numbers[1], numbers[2:]))

        return sensors

    def get_ranges(
        self, sensors: list[Sensor], target_row: int, clamp_at: int = 0
    ) -> list[range]:
        ranges = list(
            sorted(
                (r for s in sensors if (r := s.range_on_row(target_row, clamp_at))),
                key=itemgetter(0),
            )
        )
        return ranges

    @answer(5335787)
    def part_1(self) -> int:
        sensors = self.parse_sensors()
        target_row = 10 if self.use_test_data else 2000000

        ranges = self.get_ranges(sensors, target_row)

        return ranges[-1].stop - ranges[0].start

    @slow
    @answer(13673971349056)
    def part_2(self) -> int:
        sensors = self.parse_sensors()
        range_to_check = 20 if self.use_test_data else TUNING_MULTIPLIER

        for sensor in sensors:
            for point in sensor.enlarged_border_points(range_to_check):
                if any(s.can_reach(point) for s in sensors):
                    continue
                return point[0] * TUNING_MULTIPLIER + point[1]

        raise ValueError("Failed to find!")
