# prompt: https://adventofcode.com/2017/day/13

from ...base import BaseSolution, InputTypes, slow


class Solution(BaseSolution):
    _year = 2017
    _day = 13
    tree = None

    @property
    def input_type(self):
        return InputTypes.STRSPLIT

    def build_map(self, input_):
        res = {}
        for line in input_:
            location, depth = line.split(": ")
            res[int(location)] = int(depth)
        return res

    def at_zero(self, tick, depth):
        """
        returns true if at the start of this tick, the scanner is at depth 0
        """

        return tick % ((2 * depth) - 2) == 0

    def run_maze(self, start=0, exit_early=False):
        caught = []
        location = 0  # start and tick might not be the same
        for i in range(start, start + max(self.tree, key=int) + 1):
            if location in self.tree and self.at_zero(i, self.tree[location]):
                caught.append(location)
                if exit_early:
                    break
            location += 1

        return caught

    def part_1(self):
        self.tree = self.build_map(self.input)
        return sum([j * self.tree[j] for j in self.run_maze()])

    @slow
    def part_2(self):
        self.tree = self.build_map(self.input)
        while True:
            for start in range(5000000):
                caught = self.run_maze(start, exit_early=True)
                if not caught:
                    return start
