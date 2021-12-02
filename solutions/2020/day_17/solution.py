# prompt: https://adventofcode.com/2020/day/17

from collections import Counter, defaultdict
from itertools import product
from typing import Callable, DefaultDict, List, Tuple

# from functools import cache
from ...base import BaseSolution, InputTypes

COORD_OFFSETS = (-1, 0, 1)


class ConwayCube:
    cubes: DefaultDict[Tuple[int, int, int], bool]

    def __init__(self, initial_state: List[str]) -> None:
        self.cubes = defaultdict(bool)
        # read input, which is 2D
        for neg_y, line in enumerate(initial_state):
            for x, val in enumerate(line):
                self.cubes[(x, -neg_y, 0)] = val == "#"

    def _extreme_coord(self, index: int, func: Callable) -> int:
        return func({c[index] for c in self.cubes})

    @property
    def min_x(self) -> int:
        return self._extreme_coord(0, min)

    @property
    def min_y(self) -> int:
        return self._extreme_coord(1, min)

    @property
    def min_z(self) -> int:
        return self._extreme_coord(2, min)

    @property
    def max_x(self) -> int:
        return self._extreme_coord(0, max)

    @property
    def max_y(self) -> int:
        return self._extreme_coord(1, max)

    @property
    def max_z(self) -> int:
        return self._extreme_coord(2, max)

    def all_cube_coords(self):
        # +1 to be range inclusive
        return product(
            range(self.min_x, self.max_x + 1),
            range(self.min_y, self.max_y + 1),
            range(self.min_z, self.max_z + 1),
        )

    def step(self) -> None:
        next_state = defaultdict(bool)

        for coord in self.all_cube_coords():
            for cube in self.neighbors(*coord):
                num_active_neighbors = self.num_active_neighbors(*cube)
                if not self.cubes[cube] and num_active_neighbors == 3:
                    next_state[cube] = True
                elif self.cubes[cube] and num_active_neighbors not in (2, 3):
                    next_state[cube] = False
                else:
                    next_state[cube] = self.cubes[cube]

        self.cubes = next_state

    def num_active_neighbors(self, *coord) -> int:
        return len(
            [
                self.cubes[neighbor]
                # pylint: disable=no-value-for-parameter
                for neighbor in self.neighbors(*coord)
                if self.cubes[neighbor]
            ]
        )

    # pylint: disable=no-self-use
    def neighbors(self, cube_x: int, cube_y: int, cube_z: int):
        for x, y, z in product(COORD_OFFSETS, repeat=3):
            if not any([x, y, z]):
                # can't be our own neighbor
                continue
            yield (cube_x + x, cube_y + y, cube_z + z)

    def print_grid(self):
        for z in range(self.min_z, self.max_z + 1):
            print(f"\n{z=}")
            for y in reversed(range(self.min_y, self.max_y + 1)):
                for x in range(self.min_x, self.max_x + 1):
                    print("#" if self.cubes[(x, y, z)] else ".", end="")
                print()

        print()

    @property
    def num_active(self) -> int:
        return len([x for x in self.cubes.values() if x])


class Solution(BaseSolution):
    _year = 2020
    _day = 17
    input_type = InputTypes.STRSPLIT

    def part_1(self) -> int:
        return
        cubes = ConwayCube(self.input)
        for _ in range(6):
            cubes.step()
        return cubes.num_active

    def part_2(self) -> int:
        # adapted from
        # https://github.com/snoyes/AoC/blob/b688ec4d015a3a1a571ac7052d535adc4fef20ab/2020/day17.py

        def get_neighbors(cell: Tuple[int, ...]):
            neighbors = [
                tuple(cell[i] + v[i] for i in range(len(cell)))
                for v in product([-1, 0, 1], repeat=len(cell))
            ]
            neighbors.remove(cell)
            return neighbors

        def playLife(layout, dimensions=2, cycles=6):
            assert dimensions >= 2
            living = {
                (x, y) + (0,) * (dimensions - 2)
                for x, line in enumerate(layout)
                for y, _ in filter(lambda c: c[1] == "#", enumerate(line))
            }
            for _ in range(cycles):
                neighbors = Counter(
                    neighbor for cell in living for neighbor in get_neighbors(cell)
                )

                living = {
                    cell
                    for cell, times_seen in neighbors.items()
                    if times_seen == 3 or (cell in living and times_seen == 2)
                }

            return len(living)

        return playLife(self.input, dimensions=4)
