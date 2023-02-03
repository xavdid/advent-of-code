# prompt: https://adventofcode.com/2022/day/21

from operator import add, mul, sub, truediv

from ...base import StrSplitSolution, answer

OPERATIONS = {"+": add, "-": sub, "*": mul, "/": truediv}


class Solution(StrSplitSolution):
    _year = 2022
    _day = 21

    def parse_input(self):
        # untyped because exactly one item is `complex` and that's a big pain everywhere else
        settled = {}
        tbd: dict[str, str] = {}

        for line in self.input:
            name, value = line.split(": ")
            if value.isdigit():
                settled[name] = int(value)
            else:
                tbd[name] = value

        return settled, tbd

    def _solve(self, settled: dict, tbd: dict):
        while "root" not in settled:
            for name, eq in list(tbd.items()):
                l, op, r = eq.split()
                if l in settled and r in settled:
                    settled[name] = OPERATIONS[op](settled[l], settled[r])
                    tbd.pop(name)

    @answer(78342931359552)
    def part_1(self) -> int:
        settled, tbd = self.parse_input()

        self._solve(settled, tbd)

        return int(settled["root"])

    @answer(3296135418820)
    def part_2(self) -> int:
        settled, tbd = self.parse_input()

        settled["humn"] = 1j
        l, _, r = tbd["root"].split()

        self._solve(settled, tbd)
        eq, goal = settled[l], settled[r]

        return round((goal - eq.real) / eq.imag)
