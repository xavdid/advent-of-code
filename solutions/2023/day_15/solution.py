# prompt: https://adventofcode.com/2023/day/15

from collections import defaultdict

from ...base import StrSplitSolution, answer


def make_hash(ins: str) -> int:
    result = 0

    for c in ins:
        result += ord(c)
        result *= 17
        result %= 256

    return result


class Solution(StrSplitSolution):
    _year = 2023
    _day = 15

    separator = ","

    @answer(519041)
    def part_1(self) -> int:
        return sum(make_hash(ins) for ins in self.input)

    @answer(260530)
    def part_2(self) -> int:
        lenses: dict[int, dict[str, int]] = defaultdict(dict)

        for ins in self.input:
            if "-" in ins:
                label = ins[:-1]
                lenses[make_hash(label)].pop(label, None)
            elif "=" in ins:
                label, val_str = ins.split("=")
                lenses[make_hash(label)][label] = int(val_str)
            else:
                raise ValueError(f"unrecognized pattern: {ins}")

        return sum(
            sum(
                (box_id + 1) * (lense_pos + 1) * (focal_length)
                for lense_pos, focal_length in enumerate(box.values())
            )
            for box_id, box in lenses.items()
        )
