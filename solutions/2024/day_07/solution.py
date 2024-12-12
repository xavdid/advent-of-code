# prompt: https://adventofcode.com/2024/day/7

from functools import partial
from itertools import product
from multiprocessing import Pool
from operator import add, mul
from typing import Callable, Sequence

from ...base import StrSplitSolution, answer
from ...utils.transformations import parse_ints

type Operation = Callable[[int, int], int]


def process_ops(nums: list[int], ops: Sequence[Operation]) -> int:
    if len(nums) == 1:
        return nums[0]

    l, r, *rest = nums
    cur_op, *remaining_ops = ops

    return process_ops([cur_op(l, r), *rest], remaining_ops)


def concat(a: int, b: int) -> int:
    return int(str(a) + str(b))


def process_line(line: str, include_concat=False) -> int:
    target, *inputs = parse_ints(line.replace(":", "").split())

    ops = [add, mul]
    if include_concat:
        ops.append(concat)

    if any(
        process_ops(inputs, op_combo) == target
        for op_combo in product(ops, repeat=len(inputs) - 1)
    ):
        return target

    return 0


class Solution(StrSplitSolution):
    _year = 2024
    _day = 7

    @answer(12553187650171)
    def part_1(self) -> int:
        with Pool() as pool:
            return sum(pool.map(process_line, self.input))

    @answer(96779702119491)
    def part_2(self) -> int:
        # I paid for a whole CPU amd I'm gonna use all of it!
        with Pool() as pool:
            return sum(
                pool.map(
                    partial(process_line, include_concat=True),
                    self.input,
                )
            )
