# prompt: https://adventofcode.com/2021/day/12

from collections import defaultdict
from dataclasses import dataclass
from typing import Dict, List, Tuple

from ...base import StrSplitSolution, answer


@dataclass
class Path:
    steps: Tuple[str, ...]
    has_repeated_little: bool = False

    def extend_path(self, step: str) -> "Path":
        new_steps = self.steps + (step,)
        return Path(
            new_steps,
            self.has_repeated_little or (step.islower() and step in self.steps),
        )

    def can_add_step(self, step: str) -> bool:
        if step.isupper():
            return True

        if self.has_repeated_little:
            return step not in self.steps

        return True


class Solution(StrSplitSolution):
    _year = 2021
    _day = 12

    def _solve(self, can_repeat_little_cave: bool) -> int:
        connections: Dict[str, List[str]] = defaultdict(list)
        for line in self.input:
            l, r = line.split("-")
            if l != "end" and r != "start":
                connections[l].append(r)
            if l != "start" and r != "end":
                connections[r].append(l)

        in_progress_paths: List[Path] = [Path(("start",))]
        finished_paths: List[Path] = []
        next_steps: List[Path] = []

        while in_progress_paths:
            for path in in_progress_paths:
                for dest in connections[path.steps[-1]]:
                    if dest == "end":
                        finished_paths.append(path.extend_path(dest))
                        continue

                    if can_repeat_little_cave:
                        if path.can_add_step(dest):
                            next_steps.append(path.extend_path(dest))
                        continue

                    if dest.isupper() or dest not in path.steps:
                        next_steps.append(path.extend_path(dest))

            in_progress_paths = next_steps
            next_steps = []

        return len(finished_paths)

    @answer(5756)
    def part_1(self) -> int:
        return self._solve(False)

    @answer(144603)
    def part_2(self) -> int:
        return self._solve(True)
