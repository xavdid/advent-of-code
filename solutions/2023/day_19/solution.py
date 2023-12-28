# prompt: https://adventofcode.com/2023/day/19

import re
from functools import cache
from operator import gt, lt
from typing import Callable, Optional

from ...base import StrSplitSolution, answer

Part = dict[str, int]
Filter = Callable[[Part], Optional[str]]


def parse_part(line: str) -> Part:
    return {k: int(v) for k, v in re.findall(r"(.)=(\d+)", line)}


# 's<537:gd'
@cache  # doesn't actually move the needle much, but it makes sense to use
def parse_filter(m: str) -> Filter:
    category = m[0]
    op = lt if m[1] == "<" else gt
    value_str, result = m[2:].split(":")

    return lambda part: result if op(part[category], int(value_str)) else None


def build_workflow(raw_filters: str, default: str) -> Callable[[Part], str]:
    def _run_filters(part: Part) -> str:
        for raw_filter in raw_filters.split(","):
            if next_workflow := parse_filter(raw_filter)(part):
                return next_workflow

        return default

    return _run_filters


def parse_workflow(raw_workflow: str) -> tuple[str, Callable[[Part], str]]:
    if not (match := re.search(r"(.*){(.*),(.*)}", raw_workflow)):
        raise ValueError(f"unable to parse workflow: {raw_workflow}")

    key, filters, default = match.groups()

    return key, build_workflow(filters, default)


class Solution(StrSplitSolution):
    _year = 2023
    _day = 19
    separator = "\n\n"

    @answer(476889)
    def part_1(self) -> int:
        workflows_block, parts_block = self.input

        workflows = dict(
            parse_workflow(workflow_line)
            for workflow_line in workflows_block.splitlines()
        )

        def score_part(part: Part, workflow_key: str) -> int:
            if workflow_key == "A":
                return sum(part.values())
            if workflow_key == "R":
                return 0

            return score_part(part, workflows[workflow_key](part))

        return sum(
            score_part(parse_part(raw_part), "in")
            for raw_part in parts_block.splitlines()
        )

    # @answer(1234)
    def part_2(self) -> int:
        pass
