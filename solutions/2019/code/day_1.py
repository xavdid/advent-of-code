# prompt: https://adventofcode.com/2019/day/1

from typing import List

from ...base import BaseSolution, InputTypes


def calc_mass(mass: int):
    return mass // 3 - 2


class Solution(BaseSolution):
    @property
    def year(self):
        return 2019

    @property
    def number(self):
        return 1

    @property
    def input_type(self):
        return InputTypes.INTARRAY

    def part_1(self):
        return sum([calc_mass(mass) for mass in self.input])

    def part_2(self):
        res = []
        for mass in self.input:
            chain: List[int] = [calc_mass(mass)]
            while True:
                next_fuel = calc_mass(chain[-1])
                if next_fuel > 0:
                    chain.append(next_fuel)
                else:
                    break

            res.append(sum(chain))

        return sum(res)
