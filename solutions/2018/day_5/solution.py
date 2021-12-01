# prompt: https://adventofcode.com/2018/day/5

from ...base import BaseSolution, InputTypes, slow
from string import ascii_lowercase


class Solution(BaseSolution):
    _year = 2018
    _number = 5

    def is_reactive(self, a, b):
        return a.islower() != b.islower() and a.lower() == b.lower()

    def _solve(self, chars):
        def react():
            i = 0
            changed = False
            while i < len(chars) - 1:
                if self.is_reactive(chars[i], chars[i + 1]):
                    del chars[i : i + 2]
                    changed = True
                else:
                    i += 1
            return changed

        # keep calling it until nothing changes
        while react():
            pass

        return len(chars)

    def part_1(self):
        return self._solve(list(self.input.strip()))

    @slow
    def part_2(self):
        results = []
        for l in ascii_lowercase:
            # print("checking", l)
            partial = [i for i in self.input.strip() if i not in [l, l.upper()]]
            results.append(self._solve(partial))

        return min(results)
