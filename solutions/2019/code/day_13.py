# prompt: https://adventofcode.com/2019/day/13


from dataclasses import dataclass

from ...base import slow
from .intcode import STOP_REASON, IntcodeComputer, IntcodeSolution

CHARS = [" ", "X", "B", "_", "o"]


@dataclass(frozen=True)
class Point:
    # pylint: disable=invalid-name
    x: int
    y: int
    tile_type: int


class Solution(IntcodeSolution):
    @property
    def year(self):
        return 2019

    @property
    def number(self):
        return 13

    def part_1(self):
        computer = IntcodeComputer(self.input)
        computer.run()
        tiles = []
        chunk_size = 3
        for i in range(0, len(computer.output), chunk_size):
            # pylint: disable=invalid-name
            x, y, tile_type = computer.output[i : i + chunk_size]
            tiles.append(Point(x, y, tile_type))

        return len([x for x in tiles if x.tile_type == 2])

    @slow
    def part_2(self):
        # pylint: disable=invalid-name
        # the name works, but there's a little bit of input lag? so it's hard to play
        computer = IntcodeComputer(self.input)
        computer.program[0] = 2
        score = 0
        computer.run(
            num_outputs=24 * 36 * 3
        )  # screen dimensions x 3, to seed the initial outputs
        while True:
            halted = computer.run(num_outputs=3) == STOP_REASON.HALTED
            screen = {}
            chunk_size = 3
            # only really have to check new frames here, not the whole thing every time
            for i in range(0, len(computer.output), chunk_size):
                x, y, tile_type = computer.output[i : i + chunk_size]
                if x == -1 and y == 0:
                    score = tile_type
                    continue
                screen[(x, y)] = tile_type

            print("Score:", score)
            for y in range(24):
                for x in range(36):
                    print(CHARS[screen[(x, y)]], end="")
                print()

            if halted:
                break
