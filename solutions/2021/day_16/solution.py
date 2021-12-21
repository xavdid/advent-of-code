# prompt: https://adventofcode.com/2021/day/16

from typing import List
from ...base import TextSolution, answer

# from typing import Tuple


class Packet:
    def __init__(self, packet: str, subpacket_depth=0) -> None:
        self.subpacket_depth = subpacket_depth  # for debugging
        print()
        self.leveled_log(f"parsing {packet}")
        self.version = from_bin(packet[:3])
        self.type_ = from_bin(packet[3:6])
        self.leveled_log(f"{self.version=} {self.type_=}")
        self.sub_packets: List["Packet"] = []
        self.value = 0  # only used for literals
        rest = packet[6:]
        self.leveled_log(f"rest is now {rest}")
        self.packet_size = 0

        if self.is_literal:
            offset = 0
            bits = []
            while True:
                last_marker, *segment = rest[offset : offset + 5]
                bits += segment
                offset += 5
                if last_marker == "0":
                    # maybe trash bits are left in the `rest`?
                    # not sure if I need to track that
                    break

            self.value = from_bin("".join(bits))
            self.leveled_log(f"literal {self.value=}")
            # add the header; this might be wrong if i'm supposed to account for extra bits
            self.packet_size = 6 + offset

        else:
            sub_packets_by_length = rest[0] == "0"
            rest = rest[1:]

            if sub_packets_by_length:
                num_sub_packet_bits = from_bin(rest[:15])
                rest = rest[15:]
                self.leveled_log(f"operator w/ {num_sub_packet_bits} sub-packet bits")
                self.leveled_log(f"rest is now {rest}")
                read_bits = 0

                while read_bits < num_sub_packet_bits:
                    self.leveled_log("parsing subpacket")
                    sub_packet = Packet(rest, subpacket_depth=self.subpacket_depth + 1)
                    self.sub_packets.append(sub_packet)
                    read_bits += sub_packet.packet_size
                    self.leveled_log(
                        f"read {sub_packet.packet_size}, total is now {read_bits}/{num_sub_packet_bits}"
                    )
                    rest = rest[sub_packet.packet_size :]
                    self.leveled_log(f"rest is now {rest}")
                self.packet_size = 6 + 1 + 15 + num_sub_packet_bits
            else:
                num_sub_packets = from_bin(rest[:11])
                rest = rest[11:]
                self.leveled_log(f"operator w/ {num_sub_packets} sub-packets")
                self.leveled_log(f"rest is now {rest}")
                for _ in range(num_sub_packets):
                    self.leveled_log("parsing subpacket")
                    sub_packet = Packet(rest, subpacket_depth=self.subpacket_depth + 1)
                    self.sub_packets.append(sub_packet)
                    self.leveled_log("done!")
                    rest = rest[sub_packet.packet_size :]
                    self.leveled_log(f"rest is now {rest}")
                self.packet_size = (
                    6 + 1 + 11 + sum([p.packet_size for p in self.sub_packets])
                )
            self.leveled_log(f"setting packet_size to {self.packet_size}")
        self.leveled_log(f"finished parsing, final packet is {self.packet_size}")

    @property
    def is_literal(self) -> bool:
        return self.type_ == 4

    def pretty(self) -> str:
        result = f"{' ' * self.subpacket_depth}<Pkt({'L' if self.is_literal else 'O'}) vers={self.version}"  # pl={self.packet_size}
        if self.is_literal:
            result += f" val={self.value}"
        if self.sub_packets:
            result += " sub=["
            result += "".join(
                [f"\n{' '*p.subpacket_depth}{p.pretty()}" for p in self.sub_packets]
            )
            result += f'\n{" " * self.subpacket_depth}]'

        return result + ">"

    def summed_versions(self):
        return self.version + sum([p.summed_versions() for p in self.sub_packets])

    def leveled_log(self, m: str):
        return
        print(f'{" " * self.subpacket_depth}', end="")
        print(m)


def from_bin(b: str) -> int:
    return int(b, 2)


def hex_to_bits(h: str) -> str:
    return "".join([f"{int(x, 16):04b}" for x in h])


class Solution(TextSolution):
    _year = 2021
    _day = 16

    # @answer(1234)
    def part_1(self) -> int:
        p = Packet(hex_to_bits(self.input))
        self.pp(p)
        return p.summed_versions()

    # @answer(1234)
    def part_2(self) -> int:
        pass

    # @answer((1234, 4567))
    # def solve(self) -> Tuple[int, int]:
    #     pass
