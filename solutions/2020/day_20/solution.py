# prompt: https://adventofcode.com/2020/day/20

from collections import Counter
from typing import List

from ...base import BaseSolution


class Tile:
    def __init__(self, data: List[str]) -> None:
        lines = data.split("\n")

        self.num = int(lines[0].split(" ")[1][:-1])
        self.points = [tuple(line) for line in lines[1:]]

    def rotate(self) -> None:
        """
        Rotates the grid 90deg clockwise. Modifies the tile.

        https://stackoverflow.com/a/8421412/1825390
        """
        self.points = list(zip(*self.points[::-1]))

    def flip(self) -> None:
        """
        Flips a tile horizontally
        """
        for i in range(len(self.points)):
            self.points[i] = tuple(reversed(self.points[i]))

    @property
    def top_row(self) -> str:
        return "".join(self.points[0])

    def all_tops(self, skip_flip=False) -> List[str]:
        """
        Rotates and flips the tile to return each of the 8 versions of the top row.
        Modifies the tile when it runs, but has a net-zero effect on position.

        By default, does all 8 sides. Can optionally only get the non-flipped sides.
        """
        res = []
        for _ in range(4):
            res.append(self.top_row)
            self.rotate()
        if skip_flip:
            return res

        self.flip()
        for _ in range(4):
            res.append(self.top_row)
            self.rotate()
        self.flip()
        return res


class Solution(BaseSolution):
    year = 2020
    number = 20

    def part_1(self) -> int:
        tiles = [Tile(x) for x in self.input.split("\n\n")]

        c = Counter()
        for tile in tiles:
            c.update(tile.all_tops())

        result = 1
        for tile in tiles:
            # find the tiles who have 2 sides that only show up once
            if len([s for s in tile.all_tops(skip_flip=True) if c[s] == 1]) == 2:
                result *= tile.num

        return result

    def part_2(self) -> int:
        pass

    # def solve(self) -> Tuple[int, int]:
    #     pass
