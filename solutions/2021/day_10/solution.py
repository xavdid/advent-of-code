# prompt: https://adventofcode.com/2021/day/10

from typing import Iterable, List, Tuple

from ...base import StrSplitSolution, answer

OPENERS = {
    "(": ")",
    "[": "]",
    "{": "}",
    "<": ">",
}
CLOSERS_INVALID = {
    ")": 3,
    "]": 57,
    "}": 1197,
    ">": 25137,
}
CLOSERS_MATCHING = {
    ")": 1,
    "]": 2,
    "}": 3,
    ">": 4,
}


def closing_score(nums: Iterable[int]) -> int:
    score = 0
    for i in nums:
        score *= 5
        score += i
    return score


class Solution(StrSplitSolution):
    _year = 2021
    _day = 10

    @answer((464991, 3662008566))
    def solve(self) -> Tuple[int, int]:
        invalid_score = 0
        valid_line_scores: List[int] = []
        for line in self.input:
            was_valid_line = True
            incomplete_pairs: List[str] = []
            for c in line:
                if c in OPENERS:
                    incomplete_pairs.append(c)
                else:
                    if OPENERS[incomplete_pairs[-1]] != c:
                        # invalid line!
                        invalid_score += CLOSERS_INVALID[c]
                        was_valid_line = False
                        break

                    incomplete_pairs.pop()

            if was_valid_line:
                closers_needed = reversed(
                    [CLOSERS_MATCHING[OPENERS[p]] for p in incomplete_pairs]
                )
                valid_line_scores.append(closing_score(closers_needed))

        middle_score = sorted(valid_line_scores)[len(valid_line_scores) // 2]

        return invalid_score, middle_score
