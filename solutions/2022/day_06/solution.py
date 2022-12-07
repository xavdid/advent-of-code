# prompt: https://adventofcode.com/2022/day/6


from ...base import TextSolution, answer


def find_packet_start(s: str, packet_size: int) -> int:
    for i in range(packet_size, len(s)):
        if len(set(s[i - packet_size : i])) == packet_size:
            return i
    raise ValueError("not found")


class Solution(TextSolution):
    _year = 2022
    _day = 6

    @answer(1480)
    def part_1(self) -> int:
        return find_packet_start(self.input, 4)

    @answer(2746)
    def part_2(self) -> int:
        return find_packet_start(self.input, 14)
