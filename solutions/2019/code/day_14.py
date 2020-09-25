# prompt: https://adventofcode.com/2019/day/14

from collections import defaultdict
from dataclasses import dataclass
from math import ceil
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
    year = 2019
    number = 14
    input_type = InputTypes.ARRAY
    reactions: Dict[str, Reaction] = {}

    def part_1(self):
        self.reactions = {
            reaction.name: reaction
            for reaction in [Reaction(raw_reaction) for raw_reaction in self.input]
        }

        stockpile = defaultdict(int)
        unresolved_resources = defaultdict(int, {"FUEL": 1})
        total_ore_required = 0

        while unresolved_resources:
            # copy so we can change the dict while we iterate
            self.newline()
            self.newline()

            self.pp("need", unresolved_resources, "have", stockpile)

            _resource_name, num_resources_unresolved = list(
                unresolved_resources.items()
            )[0]
            reaction = self.reactions[_resource_name]

            self.newline()
            self.pp(f"working {reaction.name}")
            if reaction.is_ore_based:
                need_to_create = num_resources_unresolved - stockpile[reaction.name]
                num_reactions = ceil(need_to_create / reaction.out.amount)
                if num_reactions > 0:
                    self.pp(
                        f"have {stockpile[reaction.name]}, need {num_resources_unresolved}. I'm short {need_to_create}, which takes {num_reactions} reaction(s) that each produce {reaction.out.amount}"
                    )

                    new_ore = reaction.ore_cost * num_reactions
                    total_ore_required += new_ore
                    self.pp(
                        f"using {new_ore} more ore, total is now {total_ore_required}"
                    )

                    surplus_resources = (
                        num_reactions * reaction.out.amount
                    ) - need_to_create

                    self.pp(f"had {surplus_resources} extra")
                    stockpile[reaction.name] = surplus_resources
                else:
                    self.pp("have enough, skipping reactions", newline=True)
                    stockpile[reaction.name] -= num_resources_unresolved

                self.pp(
                    f"resolving {num_resources_unresolved} {reaction.name} ({unresolved_resources[reaction.name]} -> {unresolved_resources[reaction.name] - num_resources_unresolved})"
                )

            else:
                self.pp(f"breaking down {reaction.name}")
                for ingredient in reaction.in_:
                    self.pp(
                        f"added {ingredient.amount * ceil(num_resources_unresolved / reaction.out.amount)} {ingredient.name} ({ingredient.amount} * ceil({num_resources_unresolved} / {reaction.out.amount}))"
                    )
                    unresolved_resources[ingredient.name] += ingredient.amount * ceil(
                        num_resources_unresolved / reaction.out.amount
                    )

            del unresolved_resources[reaction.name]
            self.pp(f"removed need for {reaction.name}")

        # self.pp("before", stockpile, total_ore_required)
        # for resource, amount in stockpile.items():
        #     reaction = self.reactions[resource]
        #     while amount >= reaction.out.amount and reaction.is_ore_based:
        #         # made too many, scale it back
        #         amount -= reaction.out.amount
        #         stockpile[resource] -= reaction.out.amount  # for logging purposes
        #         total_ore_required -= reaction.ore_cost

        # self.pp("after", stockpile, total_ore_required)

        return total_ore_required

    def part_2(self):
        pass

    def solve(self):
        pass
