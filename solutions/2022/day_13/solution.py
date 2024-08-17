# prompt: https://adventofcode.com/2022/day/13

from ast import literal_eval
from functools import cmp_to_key
from itertools import zip_longest

from ...base import StrSplitSolution, answer

Packet = int | list["Packet"]


def is_ordered(left: Packet | None, right: Packet | None) -> bool | None:
    # right is smaller, not sorted
    if right is None:
        return False
    # left is smaller, sorted
    if left is None:
        return True

    if isinstance(left, int) and isinstance(right, int):
        if left == right:
            return None
        return left < right

    if isinstance(left, list) and isinstance(right, list):
        for l, r in zip_longest(left, right):
            if (res := is_ordered(l, r)) is not None:
                return res
        return None

    if isinstance(left, list):
        # list, int
        return is_ordered(left, [right])

    # int, list
    return is_ordered([left], right)


class Solution(StrSplitSolution):
    _year = 2022
    _day = 13

    separator = "\n\n"

    @answer(6272)
    def part_1(self) -> int:
        total = 0
        for index, block in enumerate(self.input):
            left, right = map(literal_eval, block.split("\n"))
            if is_ordered(left, right):
                total += index + 1

        return total

    @answer(22288)
    def part_2(self) -> int:
        divider_1: Packet = [[2]]
        divider_2: Packet = [[6]]
        flat_packets: list[Packet] = [divider_1, divider_2]
        for block in self.input:
            for packet in block.split("\n"):
                flat_packets.append(literal_eval(packet))  # noqa: PERF401

        flat_packets.sort(key=cmp_to_key(lambda l, r: -1 if is_ordered(l, r) else 1))

        return (flat_packets.index(divider_1) + 1) * (flat_packets.index(divider_2) + 1)
