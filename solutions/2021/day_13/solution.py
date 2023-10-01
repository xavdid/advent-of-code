# prompt: https://adventofcode.com/2021/day/13

import re
from typing import List, Set, Tuple, cast

from ...base import StrSplitSolution, answer

Point = Tuple[int, int]
Grid = Set[Point]

# x ->
# y
# |  0,0 1,0 2,0
# V  1,0 1,1 1,2
#    2,0 2,1 2,2


def print_grid(dots: Grid) -> None:
    max_x = max(x[0] for x in dots)
    max_y = max(y[1] for y in dots)

    for y in range(max_y + 1):
        for x in range(max_x + 1):
            print("#" if (x, y) in dots else ".", end="")
        print()
    print()


def fold_grid(dots: Grid, horiz: bool, val: int) -> Grid:
    result: Grid = set()
    modified_index, same_index = (1, 0) if horiz else (0, 1)

    for p in dots:
        # if being folded onto, no change
        if p[modified_index] < val:
            result.add(p)
            continue

        updated_point = [-1, -1]
        # one half of the points is unmodified
        updated_point[same_index] = p[same_index]

        # the other half changes based on its distance to the line
        updated_point[modified_index] = 2 * val - p[modified_index]

        result.add(cast(Point, tuple(updated_point)))

    return result


def parse_folds(folds: List[str]) -> List[Tuple[bool, int]]:
    result: List[Tuple[bool, int]] = []
    for fold in folds:
        fold_desc = re.search(r"(x|y)=(\d+)", fold)
        assert fold_desc
        result.append((fold_desc.group(1) == "y", int(fold_desc.group(2))))

    return result


message = 'ASCII art should read "PZFJHRFZ"'


class Solution(StrSplitSolution):
    _year = 2021
    _day = 13

    @answer((610, message))
    def solve(self) -> Tuple[int, str]:
        break_index = self.input.index("")
        dots: Grid = {
            cast(Point, tuple(map(int, s.split(",")))) for s in self.input[:break_index]
        }
        folds = parse_folds(self.input[break_index + 1 :])

        dots = fold_grid(dots, *folds[0])
        size_after_first_fold = len(dots)

        for fold_ins in folds[1:]:
            dots = fold_grid(dots, *fold_ins)

        print()
        print_grid(dots)
        return size_after_first_fold, message
