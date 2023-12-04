# prompt: https://adventofcode.com/2023/day/4

from collections import defaultdict

from ...base import StrSplitSolution, answer


def count_winning_numbers(line: str) -> int:
    winners, nums = line[line.index(":") + 1 :].split(" | ")

    return len(set(winners.split()) & set(nums.split()))


class Solution(StrSplitSolution):
    _year = 2023
    _day = 4

    @answer(28750)
    def part_1(self) -> int:
        return sum(
            2 ** (num_winners - 1)
            for line in self.input
            if (num_winners := count_winning_numbers(line))
        )

    @answer(10212704)
    def part_2(self) -> int:
        num_copies: defaultdict[int, int] = defaultdict(lambda: 1)

        for idx, line in enumerate(self.input):
            card_id = idx + 1  # 1-index our card numbers!
            # initialize self in defaultdict if we're not there
            num_copies[card_id]
            num_winners = count_winning_numbers(line)

            for c in range(card_id + 1, card_id + 1 + num_winners):
                num_copies[c] += num_copies[card_id]

        return sum(num_copies.values())
