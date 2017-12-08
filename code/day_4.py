# prompt: https://adventofcode.com/2017/day/4

from base import BaseSolution, InputTypes
from itertools import permutations


class Solution(BaseSolution):
    def input_type(self):
        return InputTypes.ARRAY

    def part_1(self):
        def unique(pw):
            return len(pw) == len(set(pw))

        return self.solve(unique)

    def part_2(self):
        def sans(arr, i):
            # return an array missing a single element
            if i < 0:
                raise ValueError('index must be positive, weird result otherwise')
            return arr[:i] + arr[(i + 1):]

        def anagram(pw):
            for i, phrase in enumerate(pw):
                anagrams = set([''.join(s) for s in permutations(phrase)])
                the_rest = set(sans(pw, i))
                if anagrams.intersection(the_rest):
                    return False
            return True

        return self.solve(anagram)

    def solve(self, f):
        total = 0
        for pw in self.input:
            pw = pw.split(' ')
            if f(pw):
                total += 1

        return total
