# prompt: https://adventofcode.com/2024/day/1


from collections import Counter

from ...base import StrSplitSolution, answer


class Solution(StrSplitSolution):
    _year = 2024
    _day = 1

    @answer((1223326, 21070419))
    def solve(self) -> tuple[int, int]:
        pairs = [map(int, l.split()) for l in self.input]
        l, r = [sorted(col) for col in zip(*pairs)]

        total_distance = sum(abs(a - b) for a, b in zip(l, r))

        c = Counter(r)
        similarity_score = sum(i * c.get(i, 0) for i in l)

        return total_distance, similarity_score
