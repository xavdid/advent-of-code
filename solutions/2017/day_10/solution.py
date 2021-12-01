# prompt: https://adventofcode.com/2017/day/10

from ...base import BaseSolution, InputTypes
from itertools import islice, cycle
from operator import xor
from functools import reduce


class Hahser:
    def rotate(self, l, n):
        return l[n:] + l[:n]

    def knot(self, num_rounds, input_):
        i = 0
        skip = 0
        arr = list(range(256))
        for j in range(num_rounds):
            for length in input_:
                # put my sequence first
                t = self.rotate(arr, i)

                # rotate the first `length` elements
                t[:length] = reversed(t[:length])

                # rotate it back
                arr = self.rotate(t, -i)

                # increment
                i = (i + length + skip) % len(arr)
                skip += 1

        return arr

    def densify(self, sparse):
        dense = []
        i = iter(sparse)
        while True:
            temp = list(islice(i, 16))
            if not temp:
                break
            res = hex(reduce(xor, temp))[2:]
            if len(res) == 1:
                res = "0" + res  # no good padding method?

            dense.append(res)

        return dense

    def knot_hash(self, s):
        EXTRA = [17, 31, 73, 47, 23]
        # strip is important for the trailing newline
        input_ = [ord(i) for i in s] + EXTRA
        sparse = self.knot(64, input_)

        dense = self.densify(sparse)

        return "".join(dense)


class Solution(BaseSolution, Hahser):
    _year = 2017
    _number = 10

    def part_1(self):
        input_ = [int(i) for i in self.input.split(",")]

        res = self.knot(1, input_)

        return res[0] * res[1]

    def part_2(self):
        return self.knot_hash(self.input.strip())
