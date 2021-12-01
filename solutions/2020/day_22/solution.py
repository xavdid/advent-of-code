# prompt: https://adventofcode.com/2020/day/22

from collections import deque
from typing import List, Optional, Tuple, Union

from ...base import BaseSolution

# from typing import Tuple

MaybeDeck = Union[List[int], str]


class Deck:
    def __init__(self, deck: MaybeDeck) -> None:
        if isinstance(deck, str):

            self.cards = deque(map(int, deck.split("\n")[1:]))
        else:
            self.cards = deque(deck)

    def score(self) -> int:
        max_size = len(self.cards)

        return sum(card * (max_size - index) for index, card in enumerate(self.cards))

    @property
    def top(self) -> int:
        return self.cards[0]

    @property
    def lost(self) -> bool:
        return len(self.cards) == 0

    def win_round(self, won_card: int) -> None:
        self.cards.rotate(-1)
        self.cards.append(won_card)

    @property
    def can_play_subgame(self):
        return len(self.cards) >= self.top + 1

    @property
    def subgame_deck(self) -> List[int]:
        return list(self.cards)[1 : self.top + 1]

    @property
    def frozen_deck(self) -> Tuple[int, ...]:
        return tuple(self.cards)


class Solution(BaseSolution):
    _year = 2020
    _number = 22
    next_game_num = 1

    def play_game(
        self, a: MaybeDeck, b: MaybeDeck, is_root_game=False
    ) -> Union[int, bool]:
        """
        this is a bad return type, but it's fine

        returns a `did_player_1_win` if it's a subgame, else the winner's score
        """
        player_1 = Deck(a)
        player_2 = Deck(b)

        winner: Optional[Deck] = None
        player_1_decks = set()
        player_2_decks = set()

        while winner is None:
            if (
                player_1.frozen_deck in player_1_decks
                and player_2.frozen_deck in player_2_decks
            ):
                # if we've played it before, player 1 wins
                winner = player_1
                break

            player_1_decks.add(player_1.frozen_deck)
            player_2_decks.add(player_2.frozen_deck)

            if player_1.can_play_subgame and player_2.can_play_subgame:
                # recurse
                player_1_won = self.play_game(
                    player_1.subgame_deck, player_2.subgame_deck
                )
                if player_1_won:
                    round_winner = player_1
                    round_loser = player_2
                else:
                    round_winner = player_2
                    round_loser = player_1
            elif player_1.top > player_2.top:
                # play a normal round
                round_winner = player_1
                round_loser = player_2
            else:
                round_winner = player_2
                round_loser = player_1

            round_winner.win_round(round_loser.cards.popleft())

            if round_loser.lost:
                winner = round_winner

        if is_root_game:
            return winner.score()

        return winner == player_1

    def part_1(self) -> int:
        blocks = self.input.split("\n\n")

        player_1 = Deck(blocks[0])
        player_2 = Deck(blocks[1])
        winner: Optional[Deck] = None

        while winner is None:
            if player_1.top > player_2.top:
                round_winner = player_1
                round_loser = player_2
            else:
                round_winner = player_2
                round_loser = player_1

            round_winner.win_round(round_loser.cards.popleft())

            if round_loser.lost:
                winner = round_winner

        answer = winner.score()

        assert answer == 32083
        return answer

    def part_2(self) -> int:
        blocks = self.input.split("\n\n")

        answer = self.play_game(blocks[0], blocks[1], is_root_game=True)

        assert answer == 35495
        return answer
