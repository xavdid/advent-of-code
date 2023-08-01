# prompt: https://adventofcode.com/2022/day/19

import re
from functools import reduce
from operator import add, ge, gt, le, lt, sub
from typing import Callable, Iterable, NamedTuple

from ...base import StrSplitSolution, answer


class MathTuple(NamedTuple):
    ore: int = 0
    clay: int = 0
    obsidian: int = 0
    geode: int = 0

    def increment(self, material: str) -> "MathTuple":
        return self._replace(**{material: getattr(self, material) + 1})

    def _combine(self, f: Callable[[int, int], int], other: "MathTuple"):
        return MathTuple(*(f(a, b) for a, b in zip(self, other)))

    def __add__(self, other: "MathTuple") -> "MathTuple":
        return self._combine(add, other)

    def __sub__(self, other: "MathTuple") -> "MathTuple":
        return self._combine(sub, other)

    def _comparator(self, f: Callable[[int, int], int], other: "MathTuple") -> bool:
        return all(f(a, b) for a, b in zip(self, other))

    def __lt__(self, other: "MathTuple") -> bool:
        return self._comparator(lt, other)

    def __le__(self, other: "MathTuple") -> bool:
        return self._comparator(le, other)

    def __gt__(self, other: "MathTuple") -> bool:
        return self._comparator(gt, other)

    def __ge__(self, other: "MathTuple") -> bool:
        return self._comparator(ge, other)


class Inventory(NamedTuple):
    current: MathTuple = MathTuple()
    total: MathTuple = MathTuple()

    def mine(self, robots: MathTuple) -> "Inventory":
        return Inventory(self.current + robots, self.total + robots)

    def buy(self, price: MathTuple) -> "Inventory":
        return Inventory(self.current - price, self.total)

    @property
    def key(self):
        """
        decides how an inventory is sorted.
        more promising solutions should be sorted higher
        """
        return (
            self.total.geode,
            self.total.obsidian,
            self.total.clay,
            self.total.ore,
        )


Blueprint = dict[str, MathTuple]
State = tuple[Inventory, MathTuple]

# adjust this according to how good your bounding is-
# the better the heuristic, the smaller it can be
MAX_QUEUE_SIZE = 200


def find_max_geodes(prices: Blueprint, num_minutes: int) -> int:
    queue: Iterable[State] = [(Inventory(), MathTuple(ore=1))]

    for time in range(num_minutes):
        next_queue: set[State] = set()

        if len(queue) > MAX_QUEUE_SIZE:
            queue = sorted(queue, key=lambda s: s[0].key, reverse=True)[:MAX_QUEUE_SIZE]

        # print(f"Starting round {time:02}, queue is length {len(queue):,}")

        for inventory, robots in queue:
            mined_inventory = inventory.mine(robots)

            # wait and mine
            next_queue.add((mined_inventory, robots))

            # don't build on last round
            if time == num_minutes - 1:
                continue

            # try to build each robot type and add a state for any we can afford
            for resource, price in prices.items():
                if inventory.current >= price:
                    next_queue.add(
                        (mined_inventory.buy(price), robots.increment(resource))
                    )

        queue = next_queue

    return max(i.current.geode for i, _ in queue)


class Solution(StrSplitSolution):
    _year = 2022
    _day = 19

    @answer((790, 7350))
    def solve(self) -> tuple[int, int]:
        blueprints: list[Blueprint] = []
        for line in self.input:
            costs = list(map(int, re.findall(r"(\d+) ", line)))
            blueprints.append(
                {
                    "ore": MathTuple(ore=costs[0]),
                    "clay": MathTuple(ore=costs[1]),
                    "obsidian": MathTuple(ore=costs[2], clay=costs[3]),
                    "geode": MathTuple(ore=costs[4], obsidian=costs[5]),
                }
            )

        quality_score = sum(
            (idx + 1) * find_max_geodes(prices=blueprint, num_minutes=24)
            for idx, blueprint in enumerate(blueprints)
        )

        max_geodes = reduce(
            lambda acc, blueprint: acc * find_max_geodes(blueprint, 32),
            blueprints[:3],
            1,
        )

        return quality_score, max_geodes
