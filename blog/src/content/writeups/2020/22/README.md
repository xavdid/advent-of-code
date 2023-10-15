---
year: 2020
day: 22
title: "Crab Combat"
slug: "2020/day/22"
pub_date: "2020-12-31"
---

## Part 1

Part 1 is... unexpectedly straightforward for a day 22. Honestly the tricky bit is just the repetitive code, but it's nothing we can't handle.

We'll be tracking a `list` of `int`s, but we need to do a couple of special operations. We'll need to remove the first element (top card) of the list for the losing deck and rotate the winning deck (remove the top element, put it on the bottom). As luck would have it, Python has the exact data structure for this: the `Deque`.

Pronounced just like "deck" and called so because it's a "double-ended queue". It can add and remove from either end of the list, plus it's got rotation built in. Let's build a `Deck` to hold our `deque`:

```py
class Deck:
    def __init__(self, deck: str) -> None:
        self.cards = deque(map(int, deck.split("\n")[1:]))
```

It takes one of the two input decks and handles all the parsing. We'll also add some simple utility methods that will help play the game:

```py
class Deck:
    ...

    @property
    def top(self) -> int:
        return self.cards[0]

    @property
    def lost(self) -> bool:
        return len(self.cards) == 0

    def win_round(self, won_card: int) -> None:
        self.cards.rotate(-1)
        self.cards.append(won_card)
```

Now we play! There's not much to it. We've got two variables for the decks themselves and some pointers, `round_winner` and `round_loser` that we point at each:

```py
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
```

Last is the scoring, which uses the index to get the "value" of a card:

```py
class Deck:
    ...

    def score(self) -> int:
        max_size = len(self.cards)

        return sum(card * (max_size - index) for index, card in enumerate(self.cards))

...

return winner.score()
```

## Part 2

Part 2 is the same basic idea as part 1, but with a few extra branches in the `if` statement. We'll also be recursing, so we'll copy our functionality into a function. Otherwise, it's quite similar:

```py
MaybeDeck = Union[List[int], str] # handles both input types

def play_game(
    self, a: MaybeDeck, b: MaybeDeck, is_root_game=False
) -> Union[int, bool]:
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

        # store the exact decks as tuples (which can go in sets)
        player_1_decks.add(player_1.frozen_deck)
        player_2_decks.add(player_2.frozen_deck)

        if player_1.can_play_subgame and player_2.can_play_subgame:
            # recurse
            player_1_won = self.play_game(
                player_1.subgame_deck, player_2.subgame_deck
            )
            # I wish there was a cleaner way to do this
            if player_1_won:
                round_winner = player_1
                round_loser = player_2
            else:
                round_winner = player_2
                round_loser = player_1

        # the rest is the same as part 1
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
```

In the root game, we return the winner's score. In subgames, we return "did player 1 win"? That helps us track who should win the outer game. You'll also notice some extra utility methods on the `Deck` class:

```py
class Deck:
    ...

    @property
    def can_play_subgame(self):
        return len(self.cards) >= self.top + 1

    @property
    def subgame_deck(self) -> List[int]:
        return list(self.cards)[1 : self.top + 1]

    @property
    def frozen_deck(self) -> Tuple[int, ...]:
        return tuple(self.cards)
```

The last thing is to actually call our new method and we're done:

```py
blocks = self.input.split("\n\n")

return self.play_game(blocks[0], blocks[1], is_root_game=True)
```
