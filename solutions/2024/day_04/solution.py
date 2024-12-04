# prompt: https://adventofcode.com/2024/day/4


from ...base import StrSplitSolution, answer
from ...utils.graphs import add_points, neighbors, parse_grid, subtract_points


class Solution(StrSplitSolution):
    _year = 2024
    _day = 4

    @answer(2500)
    def part_1(self) -> int:
        grid = parse_grid(self.input)

        total = 0
        for center, letter in grid.items():
            if letter != "X":
                continue

            for neighbor in neighbors(center, max_size=len(self.input) - 1):
                if grid[neighbor] != "M":
                    continue

                # we've stepped towards an M from an X. So, find our offset and keep moving in this direction.
                offset = subtract_points(neighbor, center)

                if (
                    grid.get((maybe_a := add_points(neighbor, offset))) == "A"
                    and grid.get(add_points(maybe_a, offset)) == "S"
                ):
                    total += 1

        return total

    @answer(1933)
    def part_2(self) -> int:
        grid = parse_grid(self.input)

        total = 0
        for center, letter in grid.items():
            if letter != "A":
                continue

            num_mas = 0
            for neighbor in neighbors(
                center,
                max_size=len(self.input) - 1,
                num_directions=4,
                diagonals=True,
            ):
                if grid[neighbor] != "M":
                    continue

                # we've got an M. Is there an S in the opposite direction?
                offset = subtract_points(center, neighbor)

                if grid.get(add_points(center, offset)) == "S":
                    num_mas += 1

            assert num_mas <= 2
            if num_mas == 2:
                total += 1

        return total
