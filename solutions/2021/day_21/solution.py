# prompt: https://adventofcode.com/2021/day/21

# from typing import Tuple
import re
from dataclasses import dataclass
from functools import cache
from itertools import cycle, product
from typing import Tuple, cast

from ...base import TextSolution, answer


@dataclass
class Player:
    position: int
    score = 0


BOARD = list(range(1, 10 + 1))
BOARD_SIZE = len(BOARD)


class Solution(TextSolution):
    _year = 2021
    _day = 21

    def parse_input(self) -> Tuple[Player, Player]:
        players = re.findall(r": (\d+)", self.input)
        assert len(players) == 2
        return cast(
            Tuple[Player, Player],
            tuple((Player(int(pos) - 1) for pos in players)),
        )

    @answer(897798)
    def part_1(self) -> int:
        DIE = cycle(range(1, 100 + 1))

        players = self.parse_input()
        total_rolls = 0
        player_turn = False  # booleans are ints!
        while True:
            p = players[player_turn]

            rolls = (next(DIE), next(DIE), next(DIE))
            total_rolls += 3

            p.position = (p.position + sum(rolls)) % BOARD_SIZE
            p.score += BOARD[p.position]

            if p.score >= 1000:
                return total_rolls * players[not player_turn].score

            player_turn = not player_turn

    @answer(48868319769358)
    def part_2(self) -> int:
        p1, p2 = self.parse_input()
        return max(play(p1.position, 0, p2.position, 0))


@cache
def play(ap_pos: int, ap_score: int, ip_pos: int, ip_score: int) -> Tuple[int, int]:
    """
    describes a turn between the Active Player (`ap`) and the Inactive Player (`ip`).
    """
    ap_wins, ip_wins = 0, 0

    for roll in product([1, 2, 3], repeat=3):
        new_ap_pos = (ap_pos + sum(roll)) % BOARD_SIZE
        new_ap_score = ap_score + BOARD[new_ap_pos]

        if new_ap_score >= 21:
            ap_wins += 1
        else:
            # the active player becomes inactive
            added_ip_wins, added_ap_wins = play(
                ip_pos, ip_score, new_ap_pos, new_ap_score
            )
            ap_wins += added_ap_wins
            ip_wins += added_ip_wins

    return ap_wins, ip_wins
