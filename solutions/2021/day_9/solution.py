# prompt: https://adventofcode.com/2021/day/9

from ...base import StrSplitSolution, answer

from typing import List, Set, Tuple

Point = Tuple[int, int]


class Solution(StrSplitSolution):
    _year = 2021
    _day = 9

    def neighbors(self, row: int, col: int) -> List[Point]:
        neighbors: List[Point] = []
        if col > 0:
            neighbors.append((row, col - 1))
        if col < len(self.input[row]) - 1:
            neighbors.append((row, col + 1))

        if row > 0:
            neighbors.append((row - 1, col))
        if row < len(self.input) - 1:
            neighbors.append((row + 1, col))

        return [n for n in neighbors if self.value_at(*n) != 9]

    def value_at(self, row: int, col: int) -> int:
        return int(self.input[row][col])

    answer((548, 786048))

    def solve(self) -> Tuple[int, int]:
        total = 0
        basins: List[Set[Point]] = []
        all_points: Set[Point] = set()

        for row in range(len(self.input)):
            for col in range(len(self.input[0])):
                loc = (row, col)
                if loc in all_points or self.value_at(*loc) == 9:
                    continue

                # explore this basin
                to_explore = [loc]
                basin: Set[Point] = set()
                while to_explore:
                    p = to_explore.pop()
                    if p not in basin:
                        basin.add(p)
                        to_explore += self.neighbors(*p)

                total += min(self.value_at(*p) for p in basin) + 1
                all_points.update(basin)
                basins.append(basin)

        big_basins = sorted(basins, key=len, reverse=True)[:3]
        basin_product = len(big_basins[0]) * len(big_basins[1]) * len(big_basins[2])
        return total, basin_product
