# prompt: https://adventofcode.com/2023/day/9


from ...base import StrSplitSolution, answer

NestedList = list[list[int]]


def simplify(nums: list[int]) -> NestedList:
    result = [nums]

    while True:
        last = result[-1]
        if all(e == 0 for e in last):
            return result

        result.append([r - l for l, r in zip(last, last[1:])])
        last = result[-1]


def extrapolate(layers: NestedList) -> int:
    for l, r in zip(layers[::-1], layers[::-1][1:]):
        r.append(l[-1] + r[-1])

    return layers[0][-1]


class Solution(StrSplitSolution):
    _year = 2023
    _day = 9

    def _parse_input(self) -> NestedList:
        return [list(map(int, line.split())) for line in self.input]

    def _solve(self, reverse: bool) -> int:
        histories = self._parse_input()
        return sum(extrapolate(simplify(h[::-1] if reverse else h)) for h in histories)

    @answer(1819125966)
    def part_1(self) -> int:
        return self._solve(reverse=False)

    @answer(1140)
    def part_2(self) -> int:
        return self._solve(reverse=True)
