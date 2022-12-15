# prompt: https://adventofcode.com/2022/day/14

from dataclasses import dataclass, field
from itertools import count, pairwise

from ...base import GridPoint, StrSplitSolution, answer

# Grid has everything, walls is only the initial input
# Grid = set[GridPoint]
Walls = frozenset[GridPoint]
SOURCE: GridPoint = (500, 0)


@dataclass
class Grid:
    floor: int = 0
    _grid: set[GridPoint] = field(default_factory=set)

    def add(self, p: GridPoint):
        self._grid.add(p)

    def __contains__(self, item: GridPoint):
        if self.floor:
            return item[1] >= self.floor or item in self._grid
        return item in self._grid


class Solution(StrSplitSolution):
    _year = 2022
    _day = 14

    x_min = 1000
    x_max = 0
    y_max = 0

    # only modified in parse_walls
    walls: Walls = frozenset()

    def parse_walls(self, floor: bool) -> Grid:
        grid = Grid()
        for line in self.input:
            points = [tuple(map(int, p.split(","))) for p in line.split(" -> ")]
            for (x0, y0), (x1, y1) in pairwise(points):
                self.x_min = min(self.x_min, x0, x1)
                self.x_max = max(self.x_max, x0, x1)
                self.y_max = max(self.y_max, y0, y1)

                if x0 == x1:
                    # vertical line
                    for y in range(min(y0, y1), max(y0, y1) + 1):
                        grid.add((x0, y))
                else:
                    # horizontal line
                    for x in range(min(x0, x1), max(x0, x1) + 1):
                        grid.add((x, y0))

        if floor:
            grid.floor = self.y_max + 2

        self.walls = frozenset(grid._grid)  # pylint: disable=protected-access
        return grid

    def print_grid(self, grid: Grid, floor=False):
        for y in range(self.y_max + 2 + floor):
            for x in range(self.x_min - 1, self.x_max + 2):
                p = x, y

                if p in self.walls or (floor and y == self.y_max + 2):
                    print("#", end="")
                elif p in grid:
                    print("o", end="")
                elif p == SOURCE:
                    print("+", end="")
                else:
                    print(".", end="")

            print()

    # @answer(1234)
    def part_1(self) -> int:
        floor = True
        grid = self.parse_walls(floor)
        assert self.walls
        self.pp(f"{self.x_min=} {self.x_max=} {self.y_max=}\n")
        # self.pp(grid)
        # self.print_grid(grid, floor=floor)

        for grain_num in count():
            if (500, 0) in grid:
                # self.print_grid(grid, True)
                return grain_num
            x = 500
            for y in count(1):
                # assert y < 13, "too many y"
                # falling off the world!
                # part 1 only
                if (not floor) and y > self.y_max:
                    return grain_num

                if (x, y) not in grid:
                    continue

                if (x - 1, y) not in grid:
                    x -= 1
                    continue

                if (x + 1, y) not in grid:
                    x += 1
                    continue

                self.x_min = min(self.x_min, x)
                self.x_max = max(self.x_max, x)
                grid.add((x, y - 1))
                break

            # assert grain_num < 100, "infinite loop!"

    # @answer(1234)
    def part_2(self) -> int:
        pass

    # @answer((1234, 4567))
    # def solve(self) -> tuple[int, int]:
    #     pass
