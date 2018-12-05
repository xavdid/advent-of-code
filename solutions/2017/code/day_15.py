# prompt: https://adventofcode.com/2017/day/15

from ...base import BaseSolution, InputTypes, slow


class Generator:
    mod = 2_147_483_647

    def __init__(self, start, factor, multiple):
        self.value = start
        self.factor = factor
        self.multiple = multiple

    def step(self, only_mulitples):
        self.value = (self.value * self.factor) % self.mod
        if only_mulitples and self.value % self.multiple != 0:
            return self.step(only_mulitples)

    def lowest_bits(self):
        return bin(self.value)[2:].zfill(32)[-16:]


class Solution(BaseSolution):
    @property
    def year(self):
        return 2017

    @property
    def number(self):
        return 15

    @property
    def input_type(self):
        return InputTypes.ARRAY

    def setup(self):
        starters = [int(s.split(" ")[-1]) for s in self.input]

        self.gen_a = Generator(start=starters[0], factor=16807, multiple=4)
        self.gen_b = Generator(start=starters[1], factor=48271, multiple=8)

    @slow
    def part_1(self):
        return self._solve(40_000_000, False)

    @slow
    def part_2(self):
        return self._solve(5_000_000, True)

    def _solve(self, num_pairs, only_mulitples):
        self.setup()
        total = 0
        for i in range(num_pairs):
            self.gen_a.step(only_mulitples)
            self.gen_b.step(only_mulitples)

            if self.gen_a.lowest_bits() == self.gen_b.lowest_bits():
                total += 1

        return total
