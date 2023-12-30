# prompt: https://adventofcode.com/2023/day/19

import re
from math import prod
from operator import gt, lt
from typing import Callable

from ...base import StrSplitSolution, answer

Part = dict[str, int]
RangedPart = dict[str, range]


def parse_part(line: str) -> Part:
    return {k: int(v) for k, v in re.findall(r"(.)=(\d+)", line)}


def extract_filter_components(
    f: str,
) -> tuple[str, Callable[[int, int], bool], int, str]:
    category = f[0]
    op = lt if f[1] == "<" else gt
    value_str, destination = f[2:].split(":")

    return category, op, int(value_str), destination


# part 1 returns the first matching destination
def build_workflow(raw_filters: str, default: str) -> Callable[[Part], str]:
    def _get_next_destination(part: Part):
        for raw_filter in raw_filters.split(","):
            category, op, value, destination = extract_filter_components(raw_filter)
            if op(part[category], value):
                return destination

        return default

    return _get_next_destination


def bisect_range(r: range, value: int) -> tuple[range, range]:
    """
    split a range in two at `value` (which is excluded from the bottom range but included in the top one)
    """
    return range(r.start, value), range(value, r.stop)


# part 2 cuts a bunch of ranges
def build_counting_workflow(
    raw_filters: str, default: str
) -> Callable[[RangedPart], list[tuple[str, RangedPart]]]:
    def _get_next_destinations(part: RangedPart):
        ranges: list[tuple[str, RangedPart]] = []

        for raw_filter in raw_filters.split(","):
            category, op, value, dest = extract_filter_components(raw_filter)

            if op == gt:
                keep, send = bisect_range(part[category], value + 1)
            else:
                send, keep = bisect_range(part[category], value)

            ranges.append((dest, {**part, category: send}))
            part = {**part, category: keep}

        # whatever is left also goes
        return ranges + [(default, part)]

    return _get_next_destinations


def parse_workflow[T](
    raw_workflow: str, builder: Callable[[str, str], T]
) -> tuple[str, T]:
    if not (match := re.search(r"(.*){(.*),(.*)}", raw_workflow)):
        raise ValueError(f"unable to parse workflow: {raw_workflow}")

    key, raw_filters, default = match.groups()

    return key, builder(raw_filters, default)


class Solution(StrSplitSolution):
    _year = 2023
    _day = 19
    separator = "\n\n"

    @answer(476889)
    def part_1(self) -> int:
        workflows_block, parts_block = self.input
        workflows = dict(
            parse_workflow(workflow_line, build_workflow)
            for workflow_line in workflows_block.splitlines()
        )

        def score_part(workflow_key: str, part: Part) -> int:
            if workflow_key == "R":
                return 0
            if workflow_key == "A":
                return sum(part.values())

            return score_part(workflows[workflow_key](part), part)

        return sum(
            score_part("in", parse_part(raw_part))
            for raw_part in parts_block.splitlines()
        )

    @answer(132380153677887)
    def part_2(self) -> int:
        workflows_block = self.input[0]
        workflows = dict(
            parse_workflow(workflow_line, build_counting_workflow)
            for workflow_line in workflows_block.splitlines()
        )

        def score_workflow(next_workflow: tuple[str, RangedPart]) -> int:
            workflow_key, part = next_workflow

            if workflow_key == "R":
                return 0
            if workflow_key == "A":
                return prod(len(r) for r in part.values())

            return sum(map(score_workflow, workflows[workflow_key](part)))

        return score_workflow(("in", {k: range(1, 4001) for k in "xmas"}))
