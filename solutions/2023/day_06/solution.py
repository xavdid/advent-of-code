# prompt: https://adventofcode.com/2023/day/6

from functools import reduce

from ...base import StrSplitSolution, answer


def num_race_wins(time: int, distance: int) -> int:
    return len([1 for t in range(1, time) if t * (time - t) > distance])


class Solution(StrSplitSolution):
    _year = 2023
    _day = 6

    @answer(2269432)
    def part_1(self) -> int:
        # parse the input into zipped columns
        races = zip(*(map(int, line.split()[1:]) for line in self.input))

        # multiply all the results together
        return reduce(lambda res, race: res * num_race_wins(*race), races, 1)

    @answer(35865985)
    def part_2(self) -> int:
        time, distance = [int("".join(line.split()[1:])) for line in self.input]
        return num_race_wins(time, distance)
