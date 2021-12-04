# prompt: https://adventofcode.com/2021/day/2

from ...base import StrSplitSolution, answer


class Solution(StrSplitSolution):
    _year = 2021
    _day = 2

    @answer(1714950)
    def part_1(self) -> int:
        depth = 0
        horiz = 0

        for ins in self.input:
            direction, value_str = ins.split(" ")
            value = int(value_str)
            if direction == "forward":
                horiz += value
            elif direction == "up":
                depth -= value
            elif direction == "down":
                depth += value
            else:
                raise ValueError(f'Unrecognized direction: "{direction}"')

        return depth * horiz

    @answer(1281977850)
    def part_2(self) -> int:
        depth = 0
        horiz = 0
        aim = 0

        for ins in self.input:
            direction, value_str = ins.split(" ")
            value = int(value_str)
            if direction == "forward":
                horiz += value
                depth += aim * value
            elif direction == "up":
                aim -= value
            elif direction == "down":
                aim += value
            else:
                raise ValueError(f'Unrecognized direction: "{direction}"')

        return depth * horiz

    # def solve(self) -> Tuple[int, int]:
    #     pass
