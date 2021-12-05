# prompt: https://adventofcode.com/2021/day/4

from typing import List, Set, Tuple
from ...base import StrSplitSolution, answer


class Solution(StrSplitSolution):
    _year = 2021
    _day = 4

    def parse_boards(self) -> Tuple[List[int], List[List[Set[int]]]]:
        pulls = list(map(int, self.input[0].split(",")))
        raw_boards: List[List[Tuple[int, ...]]] = [[]]
        for line in self.input[2:]:
            if line == "":
                raw_boards[-1] += [*zip(*raw_boards[-1])]
                raw_boards.append([])
                continue

            # needs to be tuple for now, so order is preserved
            raw_boards[-1].append(tuple(map(int, line.split())))

        # one last one because there's not a blank line at the end
        raw_boards[-1] += [*zip(*raw_boards[-1])]

        # make everything a set
        boards: List[List[Set[int]]] = [[set(x) for x in board] for board in raw_boards]
        return pulls, boards

    @answer(25410)
    def part_1(self) -> int:
        pulls, boards = self.parse_boards()

        for pull in pulls:
            for board in boards:
                for group in board:
                    group.discard(pull)
                    if not group:
                        # sum up all groups on this board; only do the first half
                        # of the board since the remaining numbers are duplicated
                        total = sum([sum(x) for x in board[:5]])
                        return total * pull

        raise ValueError("no solution found")

    @answer(2730)
    def part_2(self) -> int:
        pulls, boards = self.parse_boards()

        active_boards = set(range(len(boards)))
        for pull in pulls:
            for board_id, board in enumerate(boards):
                if board_id not in active_boards:
                    continue

                for group in board:
                    group.discard(pull)
                    if not group:
                        active_boards.discard(board_id)
                        if not active_boards:
                            # sum up all groups on this board; only do the first half
                            # of the board since the remaining numbers are duplicated
                            total = sum([sum(x) for x in board[:5]])
                            return total * pull

        raise ValueError("no solution found")

    # def solve(self) -> Tuple[int, int]:
    #     pass
