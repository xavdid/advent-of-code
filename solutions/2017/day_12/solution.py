# prompt: https://adventofcode.com/2017/day/12

from ...base import BaseSolution, InputTypes


class Solution(BaseSolution):
    year = 2017
    number = 12

    @property
    def input_type(self):
        return InputTypes.STRSPLIT

    def recurse_connections(self, i, res=None):
        if res is None:
            res = set()
        if i not in res:
            res.add(i)
            for n in self.tree[i]:
                self.recurse_connections(n, res)
        return res

    def build_map(self, input_):
        res = []
        for line in input_:
            nodes = line.split(" <-> ")
            res.append((int(nodes[0]), set([int(i) for i in nodes[1].split(", ")])))
        return dict(res)

    def solve(self):
        self.tree = self.build_map(self.input)

        groups = [self.recurse_connections(0)]

        already_seen = set(groups[0])

        for i in range(len(self.tree)):
            if i not in already_seen:
                groups.append(self.recurse_connections(i))
                already_seen.update(groups[-1])
                already_seen.add(i)

        return (len(groups[0]), len(groups))
