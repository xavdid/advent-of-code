# prompt: https://adventofcode.com/2023/day/25

from collections import defaultdict
from random import choice as random_choice

from ...base import StrSplitSolution, answer


class Solution(StrSplitSolution):
    _year = 2023
    _day = 25

    def sort_groups(self, graph: dict[str, set[str]]) -> int:
        ejected = random_choice(list(graph.keys()))

        right: set[str] = {ejected}
        left = set(graph) - right

        def num_right_neighbors(n: str):
            """
            for node `n`, counts how many neighbors it has in the right group
            """
            return len(graph[n] & right)

        while sum(map(num_right_neighbors, left)) != 3:
            if not left:
                # sometimes we get unlucky by ejecting a node too close to the cut point
                # in that case, just run again!
                self.debug(
                    f"got unlucky by ejecting `{ejected}` to start and didn't find a result; running again!"
                )
                return self.sort_groups(graph)

            node = max(left, key=num_right_neighbors)
            left.remove(node)
            right.add(node)

        return len(left) * len(right)

    @answer(520380)
    def part_1(self) -> int:
        """
        NOTE: adapted from https://www.reddit.com/r/adventofcode/comments/18qbsxs/2023_day_25_solutions/ketzp94/
        """
        graph: dict[str, set[str]] = defaultdict(set)
        for line in self.input:
            root, nodes = line.split(": ")
            for node in nodes.split():
                graph[root].add(node)
                graph[node].add(root)

        return self.sort_groups(graph)
