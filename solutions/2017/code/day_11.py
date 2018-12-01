# prompt: https://adventofcode.com/2017/day/11

from ...base import BaseSolution, InputTypes
from collections import defaultdict

# these totally cancel each other out
OPPOSITES = [
    ("sw", "n", "nw"),
    ("se", "n", "ne"),
    ("nw", "s", "sw"),
    ("nw", "ne", "n"),
    ("sw", "se", "s"),
    ("ne", "s", "se"),
    ("n", "s"),
    ("ne", "sw"),
    ("nw", "se"),
]


class Solution(BaseSolution):
    year = 2017
    input_type = InputTypes.STRSPLIT

    def solve(self):
        self.counts = defaultdict(int)
        max_dist = 0
        for d in self.input:
            self.counts[d] += 1
            self.cancel()
            max_dist = max(self.distance(), max_dist)

        return (self.distance(), max_dist)

    def distance(self):
        return sum(self.counts.values())

    def cancel(self):
        # cancels out opposites
        while True:
            changed = False

            for pair in OPPOSITES:
                change = min(self.counts[pair[0]], self.counts[pair[1]])
                if change:
                    changed = True

                    # don't change the result, if there is one
                    for d in pair[:2]:
                        self.counts[d] -= change

                    if len(pair) == 3:
                        self.counts[pair[2]] += change

            if not changed:
                break
