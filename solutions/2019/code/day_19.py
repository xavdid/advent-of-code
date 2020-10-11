# prompt: https://adventofcode.com/2019/day/19

from .intcode import IntcodeComputer, IntcodeSolution


class Solution(IntcodeSolution):
    year = 2019
    number = 19

    def is_in_tractor(self, x: int, y: int) -> int:
        computer = IntcodeComputer(self.input, force_uninteractive=True)
        computer.add_input([x, y])
        computer.run()
        return computer.output[-1]

    def part_1(self):

        results = 0
        for x in range(50):
            for y in range(50):
                results += self.is_in_tractor(x, y)

        return results

    def part_2(self):
        # cribbed https://www.reddit.com/r/adventofcode/comments/ecogl3/2019_day_19_solutions/fbcu8yk/
        x = 0
        y = 99
        while True:
            while not self.is_in_tractor(x, y):
                x += 1
            if self.is_in_tractor(x + 99, y - 99):
                return 10000 * x + y - 99
            y += 1
