# prompt: https://adventofcode.com/2020/day/24

from collections import Counter
from typing import List, Set, Tuple

from ...base import BaseSolution, InputTypes

Point = Tuple[int, int, int]


class Solution(BaseSolution):
    year = 2020
    number = 24
    input_type = InputTypes.STRSPLIT

    def solve(self) -> Tuple[int, int]:
        black_tiles: Set[Tuple[int, int, int]] = set()
        offsets = {
            "e": (1, -1, 0),
            "w": (-1, 1, 0),
            "se": (0, -1, 1),
            "nw": (0, 1, -1),
            "ne": (1, 0, -1),
            "sw": (-1, 0, 1),
        }

        def calculate_offset(tile: Point, offset: Point) -> Point:
            return tuple(map(sum, zip(tile, offset)))

        def neighbors(tile: Point) -> List[Point]:
            return [calculate_offset(tile, o) for o in offsets.values()]

        for line in self.input:
            tile = (0, 0, 0)
            i = 0
            while i < len(line):
                if line[i] in ["w", "e"]:
                    width = 1
                else:
                    width = 2

                tile = calculate_offset(tile, offsets[line[i : i + width]])

                i += width

            if tile in black_tiles:
                black_tiles.remove(tile)
            else:
                black_tiles.add(tile)

        part_1 = len(black_tiles)

        for _ in range(100):
            c = Counter()
            for t in black_tiles:
                c.update(neighbors(t))

            tomorrows_tiles = set()
            for tile, count in c.items():
                if tile in black_tiles and (count == 0 or count > 2):
                    # isn't stored as black
                    continue

                if tile not in black_tiles and count == 2:
                    tomorrows_tiles.add(tile)
                    continue

                if tile in black_tiles:
                    # the rest of the black tiles stay black
                    tomorrows_tiles.add(tile)

            black_tiles = tomorrows_tiles

        return part_1, len(black_tiles)
