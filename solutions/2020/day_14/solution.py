# prompt: https://adventofcode.com/2020/day/14


import re

from ...base import BaseSolution, InputTypes

int_to_padded_binary = lambda i, l=36: bin(i)[2:].rjust(l, "0")


def apply_mask_to_int(mask: str, i: int) -> str:
    return "".join(
        [
            mask_val if mask_val != "X" else target_val
            for mask_val, target_val in zip(mask, int_to_padded_binary(i))
        ]
    )


def apply_mask_to_int_v2(mask: str, i: int) -> str:
    """
    returns mask with Xs
    """
    return "".join(
        [
            target_val if mask_val == "0" else mask_val
            for mask_val, target_val in zip(mask, int_to_padded_binary(i))
        ]
    )


def resolve_floaters(mask: str) -> int:
    num_x = mask.count("X")
    num_combos = 2 ** num_x

    for i in range(num_combos):
        res = mask
        replacements = int_to_padded_binary(i, num_x)
        for digit in replacements:
            res = res.replace("X", digit, 1)  # replace one at a time
        yield int(res, 2)


class Solution(BaseSolution):
    _year = 2020
    _day = 14
    input_type = InputTypes.STRSPLIT

    def part_1(self) -> int:
        mem = {}
        mask = ""

        for line in self.input:
            if line.startswith("mask"):
                mask = line.split(" = ")[1]
            else:
                data = re.match(r"mem\[(?P<address>\d+)\] = (?P<value>\d+)", line)
                mem[data.group("address")] = int(
                    apply_mask_to_int(mask, int(data.group("value"))), 2
                )

        return sum(mem.values())

    def part_2(self) -> int:
        mem = {}
        mask = ""

        for line in self.input:
            if line.startswith("mask"):
                mask = line.split(" = ")[1]
            else:
                data = re.match(r"mem\[(?P<raw_address>\d+)\] = (?P<value>\d+)", line)

                floating_mask = apply_mask_to_int_v2(
                    mask, int(data.group("raw_address"))
                )

                for address in resolve_floaters(floating_mask):
                    mem[address] = int(data.group("value"))

        return sum(mem.values())
