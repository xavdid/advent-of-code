# prompt: https://adventofcode.com/2017/day/9

from ...base import BaseSolution, InputTypes


class Solution(BaseSolution):
    @property
    def year(self):
        return 2017

    @property
    def number(self):
        return 9

    def solve(self):
        res = 0
        garbage = False
        garbage_count = 0
        depth = 0
        i = 0
        while i < len(self.input):
            char = self.input[i]

            if char == "!":
                i += 1

            elif garbage and char != ">":
                garbage_count += 1

            elif char == "{":
                depth += 1

            elif char == "}":
                res += depth
                depth -= 1

            elif char == "<":
                garbage = True

            elif char == ">":
                garbage = False

            i += 1

        return (res, garbage_count)
