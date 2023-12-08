---
year: 2023
day: 7
title: "Camel Cards"
slug: 2023/day/7
pub_date: "2023-12-07"
---

## Part 1

At a high level, the core of today's puzzle is the sorting of hands; given a long list of hands, we need to be able to put them in an absolute order.

The most important ordering component is the `type` of the hand, so we'll need a way to represent that. After that, ties are broken by the rank of each card in the hand, left to right.

Now, a useful thing to know about Python's `tuple`s is that they're sortable! They sort based on the first element with ties getting broken by the rest of the elements (in order). Sounds useful, right? If we can represent a poker hand as a `tuple` of a hand-type-score and scores for the rest of the cards, we'll be able to sort them!

Let's start with the easy part, the tiebreakers. Each card needs a numeric value. Since we know the ordering, we can simply replace each letter with its corresponding index in a sorted list:

```py
def tiebreaker(hand: str, card_values: str) -> tuple[int, ...]:
    return tuple(card_values.index(c) for c in hand)
```

Now for the good stuff: the scoring of hands. While we could accomplish this with a class that is aware of the different hand types and knows their relative values, it's actually easier than that. A hand is defined by the number of unique cards it has _and_ the number of each of those cards. For instance, `5 of a kind` is "5 instances of 1 card", while a `full house` is "3 instances of one card and 2 instances of another".

You'll note that (for hand scoring) we don't actually care _what_ the cards are, just how many buckets they fall into. Sounds like a perfect job for `collections.Counter`! Given an iterable, it'll tell us how many of each unique item there are:

```py
Counter('T55J5') # Counter({'5': 3, 'T': 1, 'J': 1})
```

`T55J5` is a 3 of a kind, since it's got 3 of 1 thing, then 1 each of two other things. This unique patterning combined with a perennial favorite, [structural pattern matching](https://peps.python.org/pep-0636/), means we can identify each hand based on the values in a `Counter`. It inherits from `dict`, so we can get all the values with `.values()` and sort them. Once we know which hand we have, we can give better hands a higher number so they're sorted ahead of the bad ones. Here's what that looks like:

```py
def hand_to_value(hand: str) -> int:
    match sorted(Counter(hand).values()):
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
```

I like raising an error for unknown hand shapes rather than `high card` being the default. It prevents me from ended up there accidentally.

Now we have to put these together by finishing where we usually start: input parsing! For each line, we split the two halves and build a big sortable tuple along with the bid:

```py
...

class Solution(StrSplitSolution):
    def part_1(self) -> int:
        scored_hands: list[tuple[int, tuple[int, ...], int]] = []
        for line in self.input:
            hand, bid = line.split()
            scored_hands.append((hand_to_value(hand), tiebreaker(hand), int(bid)))

        return sum(
            (idx + 1) * bid for idx, (_, _, bid) in enumerate(sorted(scored_hands))
        )
```

Our scoring tuple has 3 elements: the hand type score, a 5-tuple for the card values, and an `int` for the bid. We'd be in trouble if any hands were identical (because then this approach would _also_ sort hands based on their bid), but the prompt made it sound like they'd be unique (and they were!).

Once the hands are scored, getting the actual bids is as easy as enumerating and multiplying. Destructuring lets us extract our bid, the only thing we actually need at that step.

## Part 2

Aww, those `J`s [wanna be joker](https://www.youtube.com/watch?v=yke02BDVMEA). That'll complicate things a little, but not too much! Since the two parts are so similar (and our code should be able to solve both), let's move everything into a function and add a `with_joker` arg:

```py ins={4, 8,10-11}
...

class Solution(StrSplitSolution):
    def _solve(self, with_joker: bool) -> int:
        ... # code from pt 1

    def part_1(self) -> int:
        return self._solve(with_joker=False)

    def part_2(self) -> int:
        return self._solve(with_joker=True)
```

Our `part_2` doesn't work yet, but I figure we add it while we're in there. It'll work soon!

Now, we need to adjust both of our helper functions. First, `tiebreaker`. Rather than have a single string in the function, the caller will pass its preferred scoring order in as a param. That's simple enough:

```py ins=", card_values: str" ins="card_values"
def tiebreaker(hand: str, card_values: str) -> tuple[int, ...]:
    return tuple(card_values.index(c) for c in hand)
```

Now the more interesting part: adjusting the hand score. I thought at first that a `J` would allow you to move up one hand version, but that doesn't quite hold true. If we look at the types of cards that make a hand, the most beneficial number to raise is the last one - the more of a single card you have, the better. So if any jokers exist, we should count them as part of the largest (or last) number and calculate the hand score that way. We know the jokers were included in our `Counter`, so we can remove them and add their count to the end of the hand values:

```py ins=", with_joker: bool" ins={2-5,7}
def hand_to_value(hand: str, with_joker: bool) -> int:
    hand_values = sorted(Counter(hand).values())
    if with_joker and (num_j := hand.count("J")) and num_j < 5:
        hand_values.remove(num_j)
        hand_values[-1] += num_j

    match hand_values:
        case [5]:  # 5 of a kind
            return 7
        ...
```

We only adjust the counts if we're including jokers, there _are_ any, and our hand isn't 5-of-a-kind jokers (since there's no other card count to add to). Otherwise, the rest of the function is identical.

Finally, we need slight adjustments to our core loop:

```py ins=", with_joker=with_joker" ins=", card_values" ins={5}
...

class Solution(StrSplitSolution):
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
```

And that'll do it. Happy cameling!
