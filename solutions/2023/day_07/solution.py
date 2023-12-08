# prompt: https://adventofcode.com/2023/day/7

from collections import Counter

from ...base import StrSplitSolution, answer


def tiebreaker(hand: str, card_values: str) -> tuple[int, ...]:
    return tuple(card_values.index(c) for c in hand)


def hand_to_value(hand: str, with_joker: bool) -> int:
    hand_values = sorted(Counter(hand).values())
    if with_joker and (num_j := hand.count("J")) and num_j < 5:
        hand_values.remove(num_j)
        hand_values[-1] += num_j

    match hand_values:
        case [5]:  # 5 of a kind
            return 7
        case [1, 4]:  # 4 of a kind
            return 6
        case [2, 3]:  # full house
            return 5
        case [1, 1, 3]:  # 3 of a kind
            return 4
        case [1, 2, 2]:  # 2 pair
            return 3
        case [1, 1, 1, 2]:  # 1 pair
            return 2
        case [1, 1, 1, 1, 1]:  # high card
            return 1
        case _:
            raise ValueError(f"unknown hand: {hand} ({sorted(Counter(hand).values())})")


class Solution(StrSplitSolution):
    _year = 2023
    _day = 7

    def _solve(self, with_joker: bool) -> int:
        card_values = "J23456789TQKA" if with_joker else "23456789TJQKA"

        scored_hands: list[tuple[int, tuple[int, ...], int]] = []
        for line in self.input:
            hand, bid = line.split()
            scored_hands.append(
                (
                    hand_to_value(hand, with_joker=with_joker),
                    tiebreaker(hand, card_values),
                    int(bid),
                )
            )

        return sum(
            (idx + 1) * bid for idx, (_, _, bid) in enumerate(sorted(scored_hands))
        )

    @answer(246424613)
    def part_1(self) -> int:
        return self._solve(with_joker=False)

    @answer(248256639)
    def part_2(self) -> int:
        return self._solve(with_joker=True)
