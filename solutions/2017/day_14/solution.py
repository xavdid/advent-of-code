# prompt: https://adventofcode.com/2017/day/14

from ...base import BaseSolution, InputTypes, slow
from .day_10 import Hahser


class Solution(BaseSolution, Hahser):
    year = 2017
    number = 14

    def string_to_bin(self, i):
        return bin(int(i, 16))[2:]

    def neighbors(self, point):
        row, col = point
        return [(row, col + 1), (row, col - 1), (row + 1, col), (row - 1, col)]

    @slow
    def solve(self):
        input_ = self.input.strip()
        used = []
        for i in range(128):
            key = f"{input_}-{i}"
            bin_str = str(self.string_to_bin(self.knot_hash(key))).zfill(128)
            used += [(i, idx) for idx, digit in enumerate(bin_str) if digit == "1"]

        # part 1
        total = len(used)

        # DFS
        num_groups = 0
        while len(used):
            queue = [used[0]]

            while len(queue):
                point = queue.pop()
                if point in used:
                    used.remove(point)
                    queue += self.neighbors(point)

            num_groups += 1

        return (total, num_groups)
