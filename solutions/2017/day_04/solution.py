# prompt: https://adventofcode.com/2017/day/4

from ...base import BaseSolution, InputTypes, slow
from itertools import permutations


class Solution(BaseSolution):
    _year = 2017
    _day = 4

    @property
    def input_type(self):
        return InputTypes.STRSPLIT

    def part_1(self):
        def unique(pw):
            return len(pw) == len(set(pw))

        return self._solve(unique)

    @slow
    def part_2(self):
        def sans(arr, i):
            # return an array missing a single element
            if i < 0:
                raise ValueError("index must be positive, weird result otherwise")
            return arr[:i] + arr[(i + 1) :]

        def anagram(pw):
            for i, phrase in enumerate(pw):
                anagrams = set(["".join(s) for s in permutations(phrase)])
                the_rest = set(sans(pw, i))
                if anagrams.intersection(the_rest):
                    return False
            return True

        return self._solve(anagram)

    def _solve(self, f):
        total = 0
        for pw in self.input:
            pw = pw.split(" ")
            if f(pw):
                total += 1

        return total
