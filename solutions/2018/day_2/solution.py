# prompt: https://adventofcode.com/2018/day/2

from ...base import BaseSolution, InputTypes
from itertools import combinations


class Solution(BaseSolution):
    year = 2018
    number = 2

    @property
    def input_type(self):
        return InputTypes.STRSPLIT

    def part_1(self):
        doubles = 0
        triples = 0

        for word in self.input:
            counts = {}
            for letter in word:
                if letter not in counts:
                    counts[letter] = 0

                counts[letter] += 1

            if 2 in counts.values():
                doubles += 1
            if 3 in counts.values():
                triples += 1

        return doubles * triples

    def part_2(self):
        # this is cool as hell
        # https://stackoverflow.com/a/25216366/1825390
        def differ_by_one(pair):
            combo = zip(*pair)
            return any(c1 != c2 for c1, c2 in combo) and all(
                c1 == c2 for c1, c2 in combo
            )

        # now need to find it again
        for pair in combinations(self.input, 2):
            if differ_by_one(pair):
                # need the index since it might not be the first occurance of that letter
                for idx, (i, j) in enumerate(zip(*pair)):
                    if i != j:
                        return pair[0][:idx] + pair[0][idx + 1 :]

