# prompt: https://adventofcode.com/2024/day/12


from itertools import product

from ...base import StrSplitSolution, answer
from ...utils.graphs import GridPoint, neighbors, parse_grid


class Solution(StrSplitSolution):
    _year = 2024
    _day = 12

    @answer((1483212, 897062))
    def solve(self) -> tuple[int, int]:
        grid = parse_grid(self.input)
        regions: list[set[GridPoint]] = []

        # every plant should show up in exactly one set so we track them globally
        all_points: set[GridPoint] = set()

        def matching_neighbors(point: GridPoint):
            yield from filter(
                lambda n: grid.get(n) == grid[point], neighbors(point, num_directions=4)
            )

        for point in grid:
            if point in all_points:
                continue

            # now we're standing on a new region
            region = set()

            queue = [point]
            while queue:
                cur = queue.pop()
                if cur in region:
                    continue

                region.add(cur)

                queue.extend(matching_neighbors(cur))

            all_points |= region
            regions.append(region)

        perimeter_price = 0
        side_price = 0
        for region in regions:
            perimeter = 0
            num_corners = 0

            for point in region:
                # part 1
                perimeter += 4 - len(list(matching_neighbors(point)))

                # part 2
                row, col = point

                for row_offset, col_offset in product([1, -1], repeat=2):
                    row_neighbor = (row + row_offset, col)
                    col_neighbor = (row, col + col_offset)
                    diagonal_neighbor = (row + row_offset, col + col_offset)

                    if row_neighbor not in region and col_neighbor not in region:
                        num_corners += 1

                    if (
                        row_neighbor in region
                        and col_neighbor in region
                        and diagonal_neighbor not in region
                    ):
                        num_corners += 1

            perimeter_price += perimeter * len(region)
            side_price += num_corners * len(region)

        return perimeter_price, side_price
