# prompt: https://adventofcode.com/2017/day/7

from .base import BaseSolution, InputTypes


class Answer(BaseException):
    pass


class Solution(BaseSolution):
    def input_type(self):
        return InputTypes.ARRAY

    def build_tree(self, input_):
        res = {}
        for disc in input_:
            info = disc.split(" -> ")
            name, weight = info[0].split(" ")
            weight = int(weight[1:-1])  # strip parens

            if len(info) == 2:
                # has kids
                children = info[1].split(", ")
            else:
                children = []

            res[name] = {"weight": weight, "children": children}

        return res

    def invert_tree(self, tree):
        res = {}
        for k, v in tree.items():
            if not v["children"]:
                continue

            for node in v["children"]:
                res[node] = k

        return res

    def sum_tree(self, start):
        # Throws Answer
        # Probably shouldn't use error as control flow, but it works
        weights = [self.sum_tree(child) for child in self.tree[start]["children"]]
        if weights and len(set(weights)) != 1:
            # throw the first one we find, since it's the deepest
            bad_weight_index = weights.index(self.odd_one_out(weights))
            bad_node = self.tree[start]["children"][bad_weight_index]
            imbalanced = self.tree[bad_node]["weight"]
            raise Answer(imbalanced - (max(weights) - min(weights)))

        return self.tree[start]["weight"] + sum(weights)

    def odd_one_out(self, arr):
        # returns the element that doesn't belong if there's exactly one different
        if len(arr) == 0:
            return
        elif len(arr) < 3:
            raise ValueError("unable to find odd element with less than 3")
        else:
            if arr[0] == arr[1]:
                s = set(arr)
                s.remove(arr[0])
                return s.pop()
            elif arr[0] == arr[2]:
                return arr[1]
            else:
                return arr[0]

    def part_1(self):
        tree = self.build_tree(self.input)
        parents = self.invert_tree(tree)
        k = list(parents.keys())[0]  # start anywhere, the root is there eventually
        while True:
            if k in parents:
                k = parents[k]
            else:
                break

        return k

    def part_2(self):
        self.tree = self.build_tree(self.input)
        root = self.part_1()
        try:
            self.sum_tree(root)
        except Answer as a:
            return a
