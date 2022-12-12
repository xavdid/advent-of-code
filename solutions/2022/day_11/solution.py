# prompt: https://adventofcode.com/2022/day/11

from math import lcm  # pylint: disable=no-name-in-module
from operator import add, mul
from typing import Callable, Dict

from ...base import StrSplitSolution, answer

OPS = {"+": add, "*": mul}


class Monkey:
    operation: Callable[[int], int]

    def __init__(self, raw_monkey: str) -> None:
        lines = raw_monkey.split("\n")
        self.num_inspections = 0

        # monkey id
        self.id = lines[0][7]
        # starting items
        self.items = list(map(int, lines[1].split(":")[1].split(",")))
        # operation
        operator, val = lines[2].split(" = old")[1].split()
        if val == "old":
            self.operation = lambda old: old * old
        else:
            self.operation = lambda old: OPS[operator](old, int(val))
        # test
        self.divisor = int(lines[3].split()[-1])
        # if true
        self.if_true = lines[4].split()[-1]
        # if false
        self.if_false = lines[5].split()[-1]

    def __lt__(self, other: "Monkey") -> bool:
        return self.num_inspections < other.num_inspections

    def __repr__(self) -> str:
        return f"<Monkey id={self.id=} num_inspections={self.num_inspections} items={self.items}>"


class Solution(StrSplitSolution):
    _year = 2022
    _day = 11

    separator = "\n\n"

    def parse_monkeys(self) -> Dict[str, Monkey]:
        result = {}
        for monkey in self.input:
            m = Monkey(monkey)
            result[m.id] = m
        return result

    def simulate_monkeys(
        self, num_rounds: int, worry_decreaser: int, shrinker: int | None = None
    ) -> int:
        monkeys = self.parse_monkeys()
        for _ in range(num_rounds):
            for monkey in monkeys.values():
                monkey.num_inspections += len(monkey.items)
                for item in monkey.items:
                    item = monkey.operation(item) // worry_decreaser
                    if shrinker:
                        item = item % shrinker
                    dest = (
                        monkey.if_true
                        if item % monkey.divisor == 0
                        else monkey.if_false
                    )
                    monkeys[dest].items.append(item)

                monkey.items = []

        sorted_monkeys = list(sorted(monkeys.values()))
        return sorted_monkeys[-1].num_inspections * sorted_monkeys[-2].num_inspections

    @answer(99852)
    def part_1(self) -> int:
        return self.simulate_monkeys(20, 3)

    @answer(25935263541)
    def part_2(self) -> int:
        monkeys = self.parse_monkeys()
        shrinker = lcm(*(m.divisor for m in monkeys.values()))
        return self.simulate_monkeys(10_000, 1, shrinker)
