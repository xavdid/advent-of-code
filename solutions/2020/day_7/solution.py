# prompt: https://adventofcode.com/2020/day/7


from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from ...base import BaseSolution, InputTypes


@dataclass
class HoldInfo:
    color: str
    num: int


@dataclass
class BagInfo:
    color: str
    # shortcuts
    can_hold_gold: Optional[bool] = None
    num_bags_held: Optional[int] = None
    # which bags this holds. made obsolete by num_bags_held, once calculated
    held_bags: List[HoldInfo] = field(default_factory=list)


class Solution(BaseSolution):
    _year = 2020
    _number = 7
    input_type = InputTypes.STRSPLIT
    mapping: Dict[str, BagInfo] = {}

    def can_hold_gold(self, bag) -> bool:
        bag_info = self.mapping[bag]

        if bag_info.can_hold_gold is None:
            held_bag_colors = {b.color for b in bag_info.held_bags}

            if not bag_info.held_bags:
                bag_info.can_hold_gold = False
            elif "shiny gold" in held_bag_colors:
                bag_info.can_hold_gold = True
            else:
                bag_info.can_hold_gold = any(
                    [self.can_hold_gold(color) for color in held_bag_colors]
                )

        # don't need to re-save the bag_info because it's a pointer to a dict already
        return bag_info.can_hold_gold

    def value_of_bag(self, bag) -> int:
        bag_info = self.mapping[bag]

        if bag_info.num_bags_held is None:
            bag_info.num_bags_held = 1 + sum(
                [
                    hold_info.num * self.value_of_bag(hold_info.color)
                    for hold_info in bag_info.held_bags
                ]
            )

        return bag_info.num_bags_held

    def create_mapping(self):
        for line in self.input:
            this_bag, held_bags = line.split(" bags contain ")
            bag_info = BagInfo(this_bag)

            if held_bags == "no other bags.":
                bag_info.can_hold_gold = False
                bag_info.num_bags_held = 1
                self.mapping[this_bag] = bag_info
                continue

            held_bags = held_bags.split(", ")

            for bag in held_bags:
                bag_parts = bag.split(" ")

                color = " ".join(bag_parts[1:3])
                num = int(bag_parts[0])
                bag_info.held_bags.append(HoldInfo(color, num))

            self.mapping[this_bag] = bag_info

    def solve(self) -> Tuple[int, int]:
        self.create_mapping()

        num_can_hold_gold = [self.can_hold_gold(bag) for bag in self.mapping].count(
            True
        )

        bags_in_gold = self.value_of_bag("shiny gold") - 1

        return num_can_hold_gold, bags_in_gold
