# prompt: https://adventofcode.com/2020/day/19

import re
from functools import cache  # pylint: disable=no-name-in-module

from ...base import BaseSolution


class Solution(BaseSolution):
    year = 2020
    number = 19
    rules = {}

    @cache
    def resolve_rules(self, key):
        if self.rules[key] in ("a", "b"):
            return self.rules[key]

        result = ""
        parts = self.rules[key].split(" ")
        for p in parts:
            result += "|" if p == "|" else self.resolve_rules(p)

        if "|" in result:
            result = f"({result})"

        return result

    def part_1(self) -> int:
        for line in self.input.split("\n\n")[0].split("\n"):
            key, rule = line.split(": ")
            if '"' in rule:
                # single character
                rule = rule.strip('"')

            self.rules[key] = rule

        rule_0 = self.resolve_rules("0")

        return len(
            [
                message
                for message in self.input.split("\n\n")[1].split("\n")
                if re.match(f"^{rule_0}$", message)
            ]
        )

    def part_2(self) -> int:
        pass

    # def solve(self) -> Tuple[int, int]:
    #     pass
