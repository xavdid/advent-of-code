# prompt: https://adventofcode.com/2019/day/12
import re

# from dataclasses import dataclass
from itertools import combinations
from math import gcd

from ...base import BaseSolution, InputTypes, slow

# from pprint import pprint


AXES = ["x", "y", "z"]


def lcm(a, b, c):
    # pylint: disable=invalid-name

    temp_res = (a * b) // gcd(a, b)
    return temp_res * c // gcd(temp_res, c)


# @dataclass
class Moon:
    # pos_x: int
    def __init__(self, coordinates):
        self.poisitions = {}
        self.initial_positions = {}
        self.velocities = {"x": 0, "y": 0, "z": 0}
        for var, val in re.findall(r"(.)=([-\d]*)", coordinates):
            self.poisitions[var] = int(val)
            self.initial_positions[var] = int(val)

    def __repr__(self):
        return f"<pos:{self.poisitions} | vel:{self.velocities}>"

    def __eq__(self, other):
        for axis in AXES:
            if self.poisitions[axis] != other.poisitions[axis]:
                return False
            if self.velocities[axis] != other.velocities[axis]:
                return False
        return True

    def resolve_gravity(self, other_moon, only_axis=None):
        for axis in AXES:
            if only_axis and axis != only_axis:
                continue
            if self.poisitions[axis] == other_moon.poisitions[axis]:
                continue

            if self.poisitions[axis] < other_moon.poisitions[axis]:
                self.velocities[axis] += 1
                other_moon.velocities[axis] -= 1
            else:
                self.velocities[axis] -= 1
                other_moon.velocities[axis] += 1

    def resolve_velocity(self, only_axis=None):
        for axis in AXES:
            if only_axis and axis != only_axis:
                continue
            self.poisitions[axis] += self.velocities[axis]

    def potential_energy(self):
        return sum([abs(x) for x in self.poisitions.values()])

    def kinetic_energy(self):
        return sum([abs(x) for x in self.velocities.values()])

    def total_energy(self):
        return self.potential_energy() * self.kinetic_energy()

    def has_reset(self, axis):
        return (
            self.initial_positions[axis] == self.poisitions[axis]
            and self.velocities[axis] == 0
        )


class Solution(BaseSolution):
    _year = 2019
    _day = 12

    @property
    def input_type(self):
        return InputTypes.STRSPLIT

    def part_1(self):

        moons = [Moon(coordinates) for coordinates in self.input]
        for _ in range(1000):
            for moon, other_moon in combinations(moons, 2):
                moon.resolve_gravity(other_moon)
            for moon in moons:
                moon.resolve_velocity()

        return sum([moon.total_energy() for moon in moons])

    @slow
    def part_2(self):
        # this one is hard, i'm implementing this:
        # https://www.reddit.com/r/adventofcode/comments/e9jxh2/help_2019_day_12_part_2_what_am_i_not_seeing/far9cgu/
        moons = [Moon(coordinates) for coordinates in self.input]
        cycles = []
        for axis in AXES:
            counter = 0
            while True:
                for moon, other_moon in combinations(moons, 2):
                    moon.resolve_gravity(other_moon, only_axis=axis)
                for moon in moons:
                    moon.resolve_velocity(only_axis=axis)
                counter += 1

                if all([moon.has_reset(axis) for moon in moons]):
                    break
            cycles.append(counter)

        print(cycles)
        # pylint: disable=no-value-for-parameter
        return lcm(*cycles)

    def solve(self):
        pass
