# prompt: https://adventofcode.com/2021/day/16

from functools import reduce
from operator import eq, gt, lt, mul
from typing import Callable, Dict, Iterable, List, Tuple

from ...base import TextSolution, answer


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


def product(seq: Iterable[int]) -> int:
    return reduce(mul, seq, 1)


OPERATOR_FUNCS: Dict[int, Callable[[Iterable[int]], int]] = {
    0: sum,
    1: product,
    2: min,
    3: max,
}

OPERATOR_COMPARISONS: Dict[int, Callable[[int, int], bool]] = {
    5: gt,
    6: lt,
    7: eq,
}


class Packet:
    def __init__(self, raw_packet: str) -> None:
        self.length = 0  # the number of bits in this packet
        self.value = 0
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

        else:
            if self.pop_bits(1) == "0":
                bits_read = 0
                num_bits_to_read = bin_to_int(self.pop_bits(15))

                while bits_read < num_bits_to_read:
                    bits_read += self.parse_subpacket()
            else:
                num_sub_packets = bin_to_int(self.pop_bits(11))
                for _ in range(num_sub_packets):
                    self.parse_subpacket()

            self.value = self.calculate_operator_value()

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
        return self.version + sum([p.summed_versions() for p in self.sub_packets])

    def calculate_operator_value(self) -> int:
        op = self.type

        if op in OPERATOR_FUNCS:
            return OPERATOR_FUNCS[op](p.value for p in self.sub_packets)

        assert len(self.sub_packets) == 2
        assert op in OPERATOR_COMPARISONS, f'Unknown operator: "{op}"'

        l, r = self.sub_packets
        # `int` isn't actually required here since bool is a subclass of int
        # and can be included in math operations like an int.
        # But, it's more correct looking to be explicit
        return int(OPERATOR_COMPARISONS[op](l.value, r.value))


class Solution(TextSolution):
    _year = 2021
    _day = 16

    @answer((913, 1510977819698))
    def solve(self) -> Tuple[int, int]:
        p = Packet(hex_to_bits(self.input))
        return p.summed_versions(), p.value
