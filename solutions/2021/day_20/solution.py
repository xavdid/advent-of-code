# prompt: https://adventofcode.com/2021/day/20


from typing import Dict, Literal, Tuple, Union, cast

from ...base import StrSplitSolution, answer, slow
from ...utils.graphs import GridPoint, neighbors

Marker = Union[Literal["#"], Literal["."]]
Image = Dict[GridPoint, bool]


class Solution(StrSplitSolution):
    _year = 2021
    _day = 20

    @slow
    @answer((5268, 16875))
    def solve(self) -> Tuple[int, int]:
        enhancer = {x for x in range(len(self.input[0])) if self.input[0][x] == "#"}
        # the bounds are initialized as `.`, regardless of if we swap
        if_missing = False
        # we only swap if a field of `.` should become a `#`
        should_swap = self.input[0][0] == "#"
        results = []

        # read input
        image: Image = {}
        for y, line in enumerate(self.input[2:]):
            for x, c in enumerate(line):
                image[(x, y)] = c == "#"

        # run
        for i in range(50):
            new_image: Image = {}

            for pixel in image:
                for neighbor in neighbors(pixel, 9):
                    # this line brings a 5x speed increase
                    if neighbor in new_image:
                        continue
                    result = [
                        "1" if image.get(n, if_missing) else "0"
                        for n in neighbors(neighbor, 9)
                    ]
                    new_image[neighbor] = int("".join(result), 2) in enhancer

            image = new_image

            if i in [1, 49]:
                results.append(len([x for x in image.values() if x]))
            if should_swap:
                if_missing = not if_missing

        return cast(Tuple[int, int], tuple(results))
