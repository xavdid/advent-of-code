# prompt: https://adventofcode.com/2022/day/14

from dataclasses import dataclass
from itertools import count, pairwise

from ...base import GridPoint, StrSplitSolution, answer

SOURCE: GridPoint = (500, 0)


@dataclass
class Grid:
    _grid: set[GridPoint]
    floor: int

    def add(self, p: GridPoint):
        self._grid.add(p)

    def __contains__(self, item: GridPoint):
        return item[1] >= self.floor or item in self._grid


class Solution(StrSplitSolution):
    _year = 2022
    _day = 14

    x_min = 1000
    x_max = 0
    y_max = 0

    # to differentiate walls vs sand later
    walls: frozenset[GridPoint] = frozenset()

    def parse_walls(self) -> Grid:
        grid = set()
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

        floor = self.y_max + 2
        self.walls = frozenset(grid.copy())
        return Grid(grid, floor)

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

    @answer((610, 27194))
    def solve(self) -> tuple[int, int]:
        grid = self.parse_walls()
        part_1 = -1

        for grain_num in count():
            # end of part 2
            if SOURCE in grid:
                return part_1, grain_num

            x = SOURCE[0]
            for y in count(1):
                # end of part 1
                if part_1 == -1 and y > self.y_max:
                    part_1 = grain_num

                if (x, y) not in grid:
                    continue

                if (x - 1, y) not in grid:
                    x -= 1
                    continue

                if (x + 1, y) not in grid:
                    x += 1
                    continue

                # sand is at rest
                self.x_min = min(self.x_min, x)
                self.x_max = max(self.x_max, x)
                grid.add((x, y - 1))
                break

        # to make the typechecker happy; now all branches return/error
        assert False, "shouldn't get here"
