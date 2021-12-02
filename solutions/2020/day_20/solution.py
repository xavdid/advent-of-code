# prompt: https://adventofcode.com/2020/day/20

import re
from collections import Counter
from math import sqrt
from typing import List, Set, Tuple

from ...base import BaseSolution

MONSTER_MIDDLE = r"#....##....##....###"
MONSTER_BOTTOM = r"#..#..#..#..#..#"


class Tile:
    is_corner = False
    is_edge = False

    def __init__(self, data: str) -> None:
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
    def top_side(self) -> str:
        """
        read left to right
        """
        return "".join(self.points[0])

    @property
    def bottom_side(self) -> str:
        """
        read left to right
        """
        return "".join(self.points[-1])

    @property
    def left_side(self) -> str:
        """
        read top to bottom
        """
        return "".join(x[0] for x in self.points)

    @property
    def right_side(self) -> str:
        """
        read top to bottom
        """
        return "".join(x[-1] for x in self.points)

    def get_side(self, side) -> str:
        return getattr(self, f"{side}_side")

    def all_tops(self, skip_flip=False) -> Set[str]:
        """
        Rotates and flips the tile to return each of the 8 versions of the top row.
        Modifies the tile when it runs, but has a net-zero effect on position.

        By default, does all 8 sides. Can optionally only get the non-flipped sides.
        """
        res = set()
        for _ in range(4):
            res.add(self.top_side)
            self.rotate()
        if skip_flip:
            return res

        self.flip()
        for _ in range(4):
            res.add(self.top_side)
            self.rotate()
        self.flip()
        return res

    def match_side(self, side: str, target: str) -> None:
        """
        Flips and rotates the tile until it's in the correct orientation for
        its `side` side to match the given one
        """
        for _ in range(4):
            if self.get_side(side) == target:
                return
            self.rotate()

        self.flip()
        for _ in range(4):
            if self.get_side(side) == target:
                return
            self.rotate()

        raise ValueError("Non-matching tile")

    def drop_border(self) -> List[str]:
        return ["".join(row[1:-1]) for row in self.points[1:-1]]

    def print_tile(self):
        for row in self.points:
            for column in row:
                print(column, end="")
            print()


class Image(Tile):
    """
    Tools for finding monsters
    """

    def __init__(self, data: List[str]) -> None:
        super().__init__("\n".join(["tile 0000:", *data]))
        self.stringify_points()

    def stringify_points(self) -> None:
        self.points = ["".join(line) for line in self.points]

    def rotate(self) -> None:
        super().rotate()
        self.stringify_points()

    def flip(self) -> None:
        super().flip()
        self.stringify_points()

    def each_orientation(self):
        for _ in range(4):
            self.rotate()
            yield None

        self.flip()
        for _ in range(4):
            self.rotate()
            yield None

    def find_monsters(self) -> int:
        for _ in self.each_orientation():
            res = self.count_monsters()
            if res:
                return res
        raise ValueError("Unable to find monster")

    def is_monster(self, row_num: int, tail_start: int) -> bool:
        found_head = self.points[row_num - 1][tail_start + 18] == "#"
        found_bottom = bool(
            re.match(MONSTER_BOTTOM, self.points[row_num + 1][tail_start + 1 :])
        )
        return found_head and found_bottom

    def count_monsters(self) -> int:
        # the middle of the monster can't be in the first or last line
        total = 0
        for row_num, line in enumerate(self.points[:-1]):
            # so our indexing isn't off-by-1
            if row_num == 0:
                continue

            # there might be multiple overlapping matches in a line, but most probably aren't
            # valid monsters. so we have to walk it
            i = 0
            while i < len(line):
                if line[i] != "#":
                    i += 1
                    continue
                match = re.match(MONSTER_MIDDLE, line[i:])
                if match:
                    if self.is_monster(row_num, i):
                        total += 1
                        i += 20  # total length of sea monster

                i += 1

        return total

    def count_waves(self, num_monsters):
        return sum([line.count("#") for line in self.points]) - (num_monsters * 15)


class Solution(BaseSolution):
    _year = 2020
    _day = 20
    edge_counts = Counter()
    tiles: Set[Tile] = set()

    def find_and_rotate_tile(self, side: str, target: str) -> Tile:
        for tile in self.tiles:
            if target in tile.all_tops():
                tile.match_side(side, target)
                return tile

        raise ValueError("Unable to find tile", side, target)

    def align_corner(self, tile: Tile, side_a: str, side_b: str) -> None:
        """
        Modifies the `tile` so each of the passed sides are edges
        """
        while not (
            self.edge_counts[tile.get_side(side_a)] == 1
            and self.edge_counts[tile.get_side(side_b)] == 1
        ):
            tile.rotate()

    def solve(self) -> Tuple[int, int]:
        # parse input
        self.tiles = set(Tile(x) for x in self.input.split("\n\n"))
        grid_size = int(sqrt(len(self.tiles)))  # grid is always square

        for tile in self.tiles:
            self.edge_counts.update(tile.all_tops())

        # part 1
        corner_num_product = 1
        corner_num = None
        for tile in self.tiles:
            # find the tiles who have 2 sides that only show up once
            num_outside_edges = len(
                [s for s in tile.all_tops(skip_flip=True) if self.edge_counts[s] == 1]
            )
            if num_outside_edges == 2:
                corner_num_product *= tile.num
                if corner_num is None:
                    corner_num = tile.num

        # part 2
        solved: List[List[Tile]] = []
        for row in range(grid_size):
            next_row: List[Tile] = []
            for column in range(grid_size):
                if column == 0 and row == 0:
                    # start with any corner
                    next_tile = next(t for t in self.tiles if t.num == corner_num)
                    self.align_corner(next_tile, "left", "top")
                elif column == 0:
                    next_tile = self.find_and_rotate_tile(
                        "top", solved[-1][column].bottom_side
                    )
                else:
                    next_tile = self.find_and_rotate_tile(
                        "left", next_row[-1].right_side
                    )

                self.tiles.remove(next_tile)
                next_row.append(next_tile)

            solved.append(next_row)

        # have a solved maze, in order
        # now make a list of strings that are the rows of the image.
        # Need to make one big tile we can rotate and flip until we
        # find a serpent and know that is the correct orientation

        actual_image_strs: List[str] = []
        for row in solved:
            for subrow in zip(*[t.drop_border() for t in row]):
                actual_image_strs.append("".join(subrow))

        actual_image = Image(actual_image_strs)
        num_monsters = actual_image.find_monsters()
        num_waves = actual_image.count_waves(num_monsters)

        answers = corner_num_product, num_waves
        assert answers == (29_293_767_579_581, 1989)

        return answers
