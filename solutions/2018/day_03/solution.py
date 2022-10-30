# prompt: https://adventofcode.com/2018/day/3

from ...base import BaseSolution, InputTypes, slow
import itertools


class Solution(BaseSolution):
    _year = 2018
    _day = 3

    @property
    def input_type(self):
        return InputTypes.STRSPLIT

    def parse_line(self, line):
        bits = line.split(" ")
        raw_start = bits[2].split(",")
        start = (int(raw_start[0]), int(raw_start[1][:-1]))
        size = tuple([int(i) for i in bits[3].split("x")])
        return {"id": bits[0][1:], "start": start, "size": size}

    @slow
    def solve(self):
        instructions = [self.parse_line(l) for l in self.input]
        boxes = {}
        for line in instructions:
            points = set()
            for i in range(line["start"][0], line["start"][0] + line["size"][0]):
                for j in range(line["start"][1], line["start"][1] + line["size"][1]):
                    points.add((i, j))

            boxes[line["id"]] = points

        ans = set()
        unused_ids = set(boxes)
        for a, b in itertools.combinations(boxes, 2):
            intersection = boxes[a] & boxes[b]
            if intersection:
                ans.update(intersection)
                unused_ids.discard(a)
                unused_ids.discard(b)

        return (len(ans), unused_ids.pop())
