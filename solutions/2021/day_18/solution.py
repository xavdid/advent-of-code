# prompt: https://adventofcode.com/2021/day/18

from dataclasses import dataclass
from itertools import permutations
from math import ceil, floor  # pylint: disable=no-name-in-module
from typing import List

from ...base import StrSplitSolution, answer


@dataclass
class Item:
    val: int
    depth: int


Pairs = List[Item]


def num_to_pairs(n: str) -> Pairs:
    result = []
    depth = 0
    for c in n:
        if c == "[":
            depth += 1
        if c == "]":
            depth -= 1
        if c.isnumeric():
            result.append(Item(int(c), depth))
    return result


def explode(pairs: Pairs) -> bool:
    i = 0
    while i < len(pairs):
        p = pairs[i]
        if p.depth == 5:
            if i > 0:
                pairs[i - 1].val += p.val

            if i + 2 < len(pairs):
                pairs[i + 2].val += pairs[i + 1].val

            pairs[i] = Item(0, p.depth - 1)
            # delete next element
            del pairs[i + 1]
            return True
        i += 1

    return False


def split(pairs: Pairs) -> bool:
    i = 0
    while i < len(pairs):
        p = pairs[i]
        if p.val >= 10:
            val = p.val
            depth = p.depth

            p.val = floor(val / 2)
            p.depth += 1

            pairs.insert(i + 1, Item(ceil(val / 2), depth + 1))

            return True

        i += 1
    return False


def add_and_reduce(pairs: Pairs, to_add: Pairs) -> None:
    for p in to_add:
        pairs.append(p)
    for p in pairs:
        p.depth += 1

    while True:
        if explode(pairs) or split(pairs):
            continue
        break


def magnitude(pairs: Pairs) -> int:
    while len(pairs) > 1:
        deepest_index = max(range(len(pairs)), key=lambda i: pairs[i].depth)
        deepest = pairs[deepest_index]

        left = 3 * pairs[deepest_index].val
        right = 2 * pairs[deepest_index + 1].val
        pairs[deepest_index] = Item(left + right, deepest.depth - 1)
        # the matching pair that we must know exists; it's been incorporated
        del pairs[deepest_index + 1]

    return pairs[0].val


class Solution(StrSplitSolution):
    _year = 2021
    _day = 18

    @answer(4235)
    def part_1(self) -> int:
        pairs = num_to_pairs(self.input[0])
        for line in self.input[1:]:
            add_and_reduce(pairs, num_to_pairs(line))
        return magnitude(pairs)

    @answer(4659)
    def part_2(self) -> int:
        max_res = 0
        for a, b in permutations(self.input, 2):
            pairs = num_to_pairs(a)
            add_and_reduce(pairs, num_to_pairs(b))
            res = magnitude(pairs)
            max_res = max(max_res, res)

        return max_res
