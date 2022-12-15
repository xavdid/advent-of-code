# prompt: https://adventofcode.com/2022/day/14

from itertools import count, pairwise

from ...base import GridPoint, StrSplitSolution, answer

# Grid has everything, walls is only the initial input
Grid = set[GridPoint]
Walls = frozenset[GridPoint]
SOURCE: GridPoint = (500, 0)


class Solution(StrSplitSolution):
    _year = 2022
    _day = 14

    x_min = 1000
    x_max = 0
    y_max = 0

    # only modified in parse_walls
    walls: Walls = frozenset()

    def parse_walls(self) -> Grid:
        grid: Grid = set()
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

        self.walls = frozenset(grid)
        return grid

    def print_grid(self, grid: Grid):
        for y in range(self.y_max + 2):
            for x in range(self.x_min - 1, self.x_max + 2):
                p = x, y
                if p == SOURCE:
                    print("+", end="")
                    continue

                if p in self.walls:
                    print("#", end="")
                elif p in grid:
                    print("o", end="")
                else:
                    print(".", end="")
            print()

    # @answer(1234)
    def part_1(self) -> int:
        grid = self.parse_walls()
        assert self.walls
        self.pp(f"{self.x_min=} {self.x_max=} {self.y_max=}")
        # self.pp(grid)
        # self.print_grid(grid)

        for grain_num in count():
            x = 500
            for y in count(1):
                # falling off the world!
                if y > self.y_max:
                    return grain_num

                if (x, y) not in grid:
                    continue

                if (x - 1, y) not in grid:
                    x -= 1
                    continue

                if (x + 1, y) not in grid:
                    x += 1
                    continue

                grid.add((x, y - 1))
                break

    # @answer(1234)
    def part_2(self) -> int:
        pass

    # @answer((1234, 4567))
    # def solve(self) -> tuple[int, int]:
    #     pass
