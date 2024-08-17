# prompt: https://adventofcode.com/2021/day/22

import re
from dataclasses import dataclass
from functools import reduce
from operator import mul
from typing import List, Literal, Optional, Union, cast

from ...base import StrSplitSolution, answer

signed_int = r"(-?\d+)"


def product(values: List[int]) -> int:
    return reduce(mul, values, 1)


@dataclass(frozen=True)
class Box:
    x: range
    y: range
    z: range
    on: bool = True

    @property
    def is_small(self) -> bool:
        return all(-50 <= r.start and r.stop <= 51 for r in self.ranges)  # noqa: SIM300

    @property
    def ranges(self):
        yield self.x
        yield self.y
        yield self.z

    def start(self, direction: Union[Literal["x"], Literal["y"], Literal["z"]]) -> int:
        """
        little helper to do the start-of-range that matches `.end`
        """
        return cast(range, getattr(self, direction)).start

    def end(self, direction: Union[Literal["x"], Literal["y"], Literal["z"]]) -> int:
        """
        little helper to do the end-of-range math right
        """
        return cast(range, getattr(self, direction)).stop - 1

    @property
    def volume(self) -> int:
        return product([len(r) for r in self.ranges])

    def overlap(self, other: "Box") -> Optional["Box"]:
        """
        Returns a box describing the overlap between two other boxes
        (or `None` if the boxes don't intersect)
        """
        overlap_min_x = max(self.start("x"), other.start("x"))
        overlap_max_x = min(self.end("x"), other.end("x"))
        overlap_min_y = max(self.start("y"), other.start("y"))
        overlap_max_y = min(self.end("y"), other.end("y"))
        overlap_min_z = max(self.start("z"), other.start("z"))
        overlap_max_z = min(self.end("z"), other.end("z"))

        if (
            overlap_min_x > overlap_max_x
            or overlap_min_y > overlap_max_y
            or overlap_min_z > overlap_max_z
        ):
            return None

        return Box(
            range(overlap_min_x, overlap_max_x + 1),
            range(overlap_min_y, overlap_max_y + 1),
            range(overlap_min_z, overlap_max_z + 1),
        )


def all_overlaps(root: Box, rest: List[Box]) -> List[Box]:
    """
    given a box, return a set of all of the overlaps that box has with the rest of the provided ones
    """
    result = set()
    if not rest:
        return []

    for box in rest:
        overlap = root.overlap(box)
        if overlap:
            result.add(overlap)

    return list(result)


def total_volume(boxes: List[Box]) -> int:
    if not boxes:
        return 0

    root, *rest = boxes
    if not root.on:
        return total_volume(rest)

    overlaps = all_overlaps(root, rest)

    return root.volume + total_volume(rest) - total_volume(overlaps)


class Solution(StrSplitSolution):
    _year = 2021
    _day = 22

    def parse_input(self) -> List[Box]:
        results = []
        for line in self.input:
            action, raw_bounds = line.split(" ")
            bounds = [
                map(int, x)
                for x in re.findall(rf"[xyz]={signed_int}..{signed_int}", raw_bounds)
            ]
            assert len(bounds) == 3
            results.append(
                Box(*(range(l, h + 1) for l, h in bounds), on=action == "on")
            )
        return results

    @answer(589411)
    def part_1(self) -> int:
        return total_volume([box for box in self.parse_input() if box.is_small])

    @answer(1130514303649907)
    def part_2(self) -> int:
        return total_volume(self.parse_input())
