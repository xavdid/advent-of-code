# prompt: https://adventofcode.com/2024/day/5

from graphlib import TopologicalSorter

from ...base import TextSolution, answer
from ...utils.transformations import parse_int_list


def adheres_to_rule(rule: list[int], update: list[int]) -> bool:
    assert len(rule) == 2
    l, r = rule
    if l in update and r in update:
        return update.index(l) < update.index(r)

    # if we don't have both rule items, we ignore it
    return True


def middle_element(l: list[int]) -> int:
    return l[len(l) // 2]


class Solution(TextSolution):
    _year = 2024
    _day = 5

    @answer((4996, 6311))
    def solve(self) -> tuple[int, int]:
        raw_rules, raw_updates = self.input.split("\n\n")

        rules: list[list[int]] = [
            parse_int_list(raw_rule.split("|")) for raw_rule in raw_rules.splitlines()
        ]

        updates: list[list[int]] = [
            parse_int_list(raw_update.split(","))
            for raw_update in raw_updates.splitlines()
        ]

        part_1, part_2 = 0, 0

        for update in updates:
            if all(adheres_to_rule(r, update) for r in rules):
                part_1 += middle_element(update)
            else:
                sorter = TopologicalSorter()
                for l, r in rules:
                    if l in update and r in update:
                        sorter.add(l, r)

                fixed_update = list(sorter.static_order())

                part_2 += middle_element(fixed_update)

        return part_1, part_2
