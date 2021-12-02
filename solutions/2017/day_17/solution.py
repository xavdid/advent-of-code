# prompt: https://adventofcode.com/2017/day/17

from ...base import BaseSolution, InputTypes, slow


class Solution(BaseSolution):
    _year = 2017
    _day = 17

    @property
    def input_type(self):
        return InputTypes.INTEGER

    def part_1(self):
        return self._solve(2017, 2017)

    @slow
    def part_2(self):
        # too slow!
        # return self._solve(50000000, 0)

        # we don't actually  have to store the list, 0 is always "first"
        res = None
        pos = 0
        for i in range(1, 50000000 + 1):
            pos = (pos + self.input) % i
            if pos == 0:
                res = i
            pos += 1

        return res

    def _solve(self, end, find):
        b = [0]
        pos = 0

        for i in range(1, end + 1):
            pos = (pos + self.input) % len(b)
            if pos + 1 == len(b):
                b.append(i)
            else:
                b.insert(pos + 1, i)
            pos += 1

        idx = b.index(end)
        return b[idx + 1]
