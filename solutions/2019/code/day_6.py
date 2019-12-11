# prompt: https://adventofcode.com/2019/day/6

from ...base import BaseSolution, InputTypes


class Solution(BaseSolution):
    @property
    def year(self):
        return 2019

    @property
    def number(self):
        return 6

    @property
    def input_type(self):
        return InputTypes.ARRAY

    def get_orbits(self):
        orbits = {}
        for orbit in self.input:
            [this_is_orbited_by, this_one] = orbit.split(")")
            orbits[this_one] = this_is_orbited_by  # 1 to 1
        return orbits

    def part_1(self):
        orbits = self.get_orbits()
        counts = {}
        counts["COM"] = 0

        def calulate_value_of(planet):
            if planet in counts:
                return counts[planet]
            res = calulate_value_of(orbits[planet]) + 1
            counts[planet] = res
            return res

        for planet in orbits:
            calulate_value_of(planet)

        return sum(counts.values())

    def part_2(self):
        orbits = self.get_orbits()

        def path_to_com(start):
            res = [start]
            while res[-1] != "COM":
                res.append(orbits[res[-1]])
            return res[1:]  # drop start

        # they both end at the same place, so clip the end until they diverge.
        # Then we'll have the path to get to each end point from their common ancestor
        you_path = path_to_com("YOU")
        san_path = path_to_com("SAN")

        while you_path[-1] == san_path[-1]:
            you_path.pop()
            san_path.pop()

        return len(you_path) + len(san_path)
