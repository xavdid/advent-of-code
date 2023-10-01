# prompt: https://adventofcode.com/2019/day/14

from collections import defaultdict
from dataclasses import dataclass
from math import ceil
from os import name
from typing import Dict, List, Tuple, Union

from ...base import BaseSolution, InputTypes


@dataclass(eq=True, frozen=True)
class Reagent:
    name: str
    amount: int

    @classmethod
    def from_string(cls, reagent_input: str) -> "Reagent":
        amount, name = reagent_input.strip().split(" ")

        return Reagent(name, int(amount))


@dataclass
class Reaction:
    out: Reagent
    in_: List[Reagent]

    def __init__(self, raw_reaction: str) -> None:
        # 3 A, 4 B => 1 AB
        in_, out = raw_reaction.split("=>")

        self.out = Reagent.from_string(out)
        self.in_ = [Reagent.from_string(x) for x in in_.split(",")]

    @property
    def name(self):
        return self.out.name

    @property
    def is_ore_based(self):
        return self.in_[0].name == "ORE"

    @property
    def ore_cost(self):
        if not self.is_ore_based:
            raise TypeError("Unable to calculate ore count of non-ore reaction")
        return self.in_[0].amount


class Solution(BaseSolution):
    _year = 2019
    _day = 14
    input_type = InputTypes.STRSPLIT
    reactions: Dict[str, Reaction] = {}

    def ore_cost_for_n_fuel(self, num_fuel):
        self.reactions = {
            reaction.name: reaction
            for reaction in [Reaction(raw_reaction) for raw_reaction in self.input]
        }

        stockpile = defaultdict(int)
        unresolved_resources = defaultdict(int, {"FUEL": num_fuel})
        total_ore_required = 0

        while unresolved_resources:
            # copy so we can change the dict while we iterate
            self.debug(trailing_newline=True)
            self.debug(trailing_newline=True)

            self.debug("need", unresolved_resources, "have", stockpile)

            _resource_name, num_resources_unresolved = list(
                unresolved_resources.items()
            )[0]
            reaction = self.reactions[_resource_name]

            self.debug(
                f"working {_resource_name}; have {stockpile[reaction.name]}, need {unresolved_resources[reaction.name]}"
            )

            need_to_create = num_resources_unresolved - stockpile[reaction.name]

            if need_to_create <= 0:
                stockpile[reaction.name] -= unresolved_resources[reaction.name]
                self.debug(
                    f"no reaction needed, stockpile is now {stockpile[reaction.name]}"
                )
                del unresolved_resources[reaction.name]
                continue

            # have too few, must create
            self.debug(f"resolving {reaction.name}, clearing stockpile")
            del unresolved_resources[reaction.name]
            del stockpile[reaction.name]

            num_reactions = ceil(need_to_create / reaction.out.amount)
            extra = (num_reactions * reaction.out.amount) - need_to_create
            # this reaction hasn't happened yet, but any surplus we create here could enable downstream reactions to produce less
            # tracking this extra was what I wasn't doing before
            # cheers to https://0xdf.gitlab.io/adventofcode2019/14#part-1 for the tip
            stockpile[reaction.name] += extra
            self.debug(
                f"doing {num_reactions} reaction(s) (each producing {reaction.out.amount}) to fulfill above, leaving {extra} extra"
            )

            if reaction.is_ore_based:
                total_ore_required += num_reactions * reaction.ore_cost
                self.debug(
                    f"that cost {num_reactions * reaction.ore_cost} ore, total is now {total_ore_required}"
                )
            else:
                self.debug("not an ore reaction!")
                for reagent in reaction.in_:
                    self.debug(
                        f"adding {reaction.name} depedency on {reagent.name} (need {reagent.amount * num_reactions})"
                    )
                    unresolved_resources[reagent.name] += reagent.amount * num_reactions

        return total_ore_required

    def part_1(self):
        return self.ore_cost_for_n_fuel(1)

    def part_2(self):
        # need to find the input that gives output that's closest to this without going over
        # binary search!
        target = 1_000_000_000_000
        result = 0

        low = 1
        high = target
        mid = 0

        while low <= high:
            mid = (low + high) // 2
            result = self.ore_cost_for_n_fuel(mid)

            # unlikely, but possible
            if result == target:
                return mid

            if result > target:
                high = mid - 1
            else:
                low = mid + 1

        return mid
