# prompt: https://adventofcode.com/2020/day/24

from typing import Set, Tuple

from ...base import BaseSolution, InputTypes

# from typing import Tuple


class Solution(BaseSolution):
    year = 2020
    number = 24
    input_type = InputTypes.STRSPLIT

    def part_1(self) -> int:
        black_tiles: Set[Tuple[int, int, int]] = set()
        offsets = {
            "e": (1, -1, 0),
            "w": (-1, 1, 0),
            "se": (0, -1, 1),
            "nw": (0, 1, -1),
            "ne": (1, 0, -1),
            "sw": (-1, 0, 1),
        }

        for line in self.input:
            tile = (0, 0, 0)
            i = 0
            while i < len(line):
                if line[i] in ["w", "e"]:
                    width = 1
                else:
                    width = 2

                tile = tuple(map(sum, zip(tile, offsets[line[i : i + width]])))

                i += width

            if tile in black_tiles:
                black_tiles.remove(tile)
            else:
                black_tiles.add(tile)

        return len(black_tiles)

    def part_2(self) -> int:
        pass

    # def solve(self) -> Tuple[int, int]:
    #     pass
