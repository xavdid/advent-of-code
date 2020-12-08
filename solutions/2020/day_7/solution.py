# prompt: https://adventofcode.com/2020/day/7


from dataclasses import dataclass
from typing import Optional

from ...base import BaseSolution, InputTypes


@dataclass
class BagStats:
    can_hold_gold: Optional[bool] = None
    num_bags_in: Optional[int] = None


class Solution(BaseSolution):
    year = 2020
    number = 7
    input_type = InputTypes.STRSPLIT

    def can_hold_gold(self, bag) -> bool:
        if isinstance(self.mapping[bag], bool):
            return self.mapping[bag]

        if not self.mapping[bag]:
            res = False
        elif "shiny gold" in self.mapping[bag]:
            res = True
        else:
            res = any([self.can_hold_gold(color) for color in self.mapping[bag]])

        # cache results for later
        self.mapping[bag] = res
        return res

    def num_bags_in(self, bag):
        pass

    def part_1(self) -> int:
        self.mapping = {}
        for line in self.input:
            this_bag, held_bags = line.split(" bags contain ")
            if held_bags == "no other bags.":
                self.mapping[this_bag] = []
                continue

            held_bags = held_bags.split(", ")

            these_bags = []
            # just grab the adjective and color
            for bag in held_bags:
                bag_parts = bag.split(" ")
                these_bags.append(" ".join(bag_parts[1:3]))

            self.mapping[this_bag] = these_bags

        return [self.can_hold_gold(bag) for bag in self.mapping].count(True)

    def part_2(self) -> int:
        pass


#   def solve(self) -> Tuple[int, int]:
#       pass
