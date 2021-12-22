# prompt: https://adventofcode.com/2021/day/16

from typing import List
from ...base import TextSolution, answer

# from typing import Tuple


def bin_to_int(b: str) -> int:
    """
    '1101' -> 13
    """
    return int(b, 2)


def hex_to_bits(h: str) -> str:
    """
    'D2FE28' -> '110100101111111000101000'

    For each hex letter, returns a padded 4-bit binary string
    """
    return "".join([f"{int(x, 16):0>4b}" for x in h])


class Packet:
    def __init__(self, raw_packet: str) -> None:
        self.length = 0  # the number of bits in this packet
        self.value = 0  # only used for literals
        self.sub_packets: List["Packet"] = []
        self.raw_packet = raw_packet

        self.version = bin_to_int(self.pop_bits(3))
        self.type = bin_to_int(self.pop_bits(3))

        if self.is_literal:
            value_bits = []
            while True:
                last_marker, *segment = self.pop_bits(5)
                value_bits += segment
                if last_marker == "0":
                    break

            self.value = bin_to_int("".join(value_bits))

        elif self.pop_bits(1) == "0":
            bits_read = 0
            num_bits_to_read = bin_to_int(self.pop_bits(15))

            while bits_read < num_bits_to_read:
                bits_read += self.parse_subpacket()
        else:
            num_sub_packets = bin_to_int(self.pop_bits(11))
            for _ in range(num_sub_packets):
                self.parse_subpacket()

    def pop_bits(self, num_bits: int) -> str:
        result = self.raw_packet[:num_bits]
        self.raw_packet = self.raw_packet[num_bits:]
        self.length += num_bits
        return result

    def parse_subpacket(self) -> int:
        sub_packet = Packet(self.raw_packet)
        self.sub_packets.append(sub_packet)
        self.pop_bits(sub_packet.length)
        return sub_packet.length

    @property
    def is_literal(self) -> bool:
        return self.type == 4

    def summed_versions(self):
        """
        Used for part 1
        """
        return self.version + sum([p.summed_versions() for p in self.sub_packets])


class Solution(TextSolution):
    _year = 2021
    _day = 16

    @answer(913)
    def part_1(self) -> int:
        return Packet(hex_to_bits(self.input)).summed_versions()

    # @answer(1234)
    def part_2(self) -> int:
        pass

    # @answer((1234, 4567))
    # def solve(self) -> Tuple[int, int]:
    #     pass
