# prompt: https://adventofcode.com/2020/day/19

import re
from typing import Tuple

from ...base import BaseSolution


class Solution(BaseSolution):
    year = 2020
    number = 19
    rules = {}
    num_loops = {"8": 0, "11": 0}  # detects loops

    def resolve_rules(self, key):
        if key in self.num_loops:
            # after 6 levels, the answers stop changing
            if self.num_loops[key] == 6:
                return ""
            self.num_loops[key] += 1

        if self.rules[key] in ("a", "b"):
            return self.rules[key]

        result = ""
        parts = self.rules[key].split(" ")
        for p in parts:
            result += "|" if p == "|" else self.resolve_rules(p)

        if "|" in result:
            result = f"({result})"

        return result

    def solve(self) -> Tuple[int, int]:
        for line in self.input.split("\n\n")[0].split("\n"):
            key, rule = line.split(": ")
            if '"' in rule:
                # single character
                rule = rule.strip('"')

            self.rules[key] = rule

        messages = self.input.split("\n\n")[1].split("\n")

        rule_0 = self.resolve_rules("0")
        part_1 = len(
            [message for message in messages if re.match(f"^{rule_0}$", message)]
        )

        self.rules["8"] = "42 | 42 8"
        self.rules["11"] = "42 31 | 42 11 31"

        rule_0 = self.resolve_rules("0")
        part_2 = len(
            [message for message in messages if re.match(f"^{rule_0}$", message)]
        )

        return part_1, part_2
