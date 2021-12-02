# prompt: https://adventofcode.com/2019/day/24

from collections import Counter
from enum import Enum
from typing import List, Tuple

from ...base import BaseSolution, InputTypes

# pylint: disable=invalid-name


#    y, x
#
#    0 x-> 5
#    y ....#
#    | #..#.
#    V #..##
#      ..#..
#    5 #....


def index_from_grid(y, x):
    return x + y * 5


def flatten(l: List[List[any]]):
    return [item for sublist in l for item in sublist]


def map_to_str(enum_list):
    return "".join([x.value for x in flatten(enum_list)])


class TILES(Enum):
    BUG = "#"
    EMPTY = "."


def biodiversity(map_str: str) -> int:
    total = 0
    for index, char in enumerate(map_str):
        if TILES(char) == TILES.BUG:
            total += 2 ** index
    return total


class Planet:
    def __init__(self, lines: List[List[str]]) -> None:
        self.map = [list(map(TILES, line)) for line in lines]
        self.configurations = {map_to_str(self.map)}

    def print(self):
        for y in range(5):
            for x in range(5):
                print(self.map[y][x].value, end="")
            print()

    def compute(self):
        while True:
            result = self.step()
            if result:
                return result

    def step(self):
        result = []
        for y in range(5):
            _r = []
            for x in range(5):
                char = self.map[y][x]
                adjacent_chars = self.adjacent_chars(y, x)

                if char == TILES.BUG and adjacent_chars[TILES.BUG] != 1:
                    _r.append(TILES.EMPTY)
                elif char == TILES.EMPTY and (0 < adjacent_chars[TILES.BUG] <= 2):
                    _r.append(TILES.BUG)
                else:
                    _r.append(char)
            result.append(_r)

        map_str = map_to_str(result)
        if map_str in self.configurations:
            return biodiversity(map_str)

        self.map = result
        self.configurations.add(map_str)
        return None

    def adjacent_chars(self, y, x):
        return Counter(
            map(self.char_at, [(y, x + 1), (y, x - 1), (y + 1, x), (y - 1, x)])
        )

    def char_at(self, point: Tuple[int, int]):
        y, x = point
        try:
            if not ((0 <= y <= 5) and (0 <= x <= 5)):
                raise IndexError
            return self.map[y][x]
        except IndexError:
            return TILES.EMPTY


class Solution(BaseSolution):
    _year = 2019
    _day = 24
    input_type = InputTypes.STRSPLIT

    def part_1(self):
        planet = Planet(self.input)
        return planet.compute()

    def part_2(self):
        pass

    def solve(self):
        pass
