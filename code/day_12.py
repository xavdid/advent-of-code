# prompt: https://adventofcode.com/2017/day/12

from base import BaseSolution, InputTypes


class Solution(BaseSolution):
    def input_type(self):
        return InputTypes.ARRAY

    def part_1(self):
        self.tree = self.build_map(self.input)
        self.connected_to_0 = set()

        self.recurse_connections(0)
        return len(self.connected_to_0)

    def recurse_connections(self, i):
        if i not in self.connected_to_0:
            self.connected_to_0.add(i)
            for n in self.tree[i]:
                self.add_to_set(n)

    def build_map(self, input_):
        res = []
        for line in input_:
            nodes = line.split(" <-> ")
            res.append((int(nodes[0]), set([int(i) for i in nodes[1].split(", ")])))
        return dict(res)

    def part_2(self):
        pass

    def solve(self, f):
        pass
