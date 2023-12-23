---
year: 2023
day: 4
title: "Scratchcards"
slug: 2023/day/4
pub_date: "2023-12-03"
---

## Part 1

Another part 1 where the bulk of the work is just parsing the input. At least so far, we don't care about the `Card N:` label, since (if/when we need it) we can get that info from the index. That leaves us with two space-separated lists groups of numbers that we need to find overlaps between. Python's `set` class is perfect for this! Used in conjunction with `&` shows you all the overlapping elements, the size of which is the number of winning numbers we need:

```py
def count_winning_numbers(line: str) -> int:
    # ignore everything before the `:`
    winners, nums = line[line.index(":") + 1 :].split(" | ")

    # return the size of the overlap between the two sets
    return len(set(winners.split()) & set(nums.split()))
```

Next, we need to call that on each line and do some math. The fact that the score doubles repeatedly means we can calculate the score with 2<sup>`N`</sup>. For our purposes, `N` is 1 less than the number of winners (since 1 winning number is worth 1 point and 2<sup>0</sup> is `1`). That code is delightfully simple:

```py
...

class Solution(StrSplitSolution):
    def part_1(self) -> int:
        total = 0

        for line in self.input:
            if num_winners := count_winning_numbers(line):
                total += 2 ** (num_winners - 1)

        return total
```

We can condense this further (but still make it readable) using a comprehension and a filter:

```py
return sum(
    2 ** (num_winners - 1)
    for line in self.input
    if (num_winners := count_winning_numbers(line))
)
```

## Part 2

I had to read this prompt 3 times and I still didn't quite follow it. When I get to that point, I just start implementing the steps in the prompt very literally and see where it gets me, which ended up working on this one.

To start off, we'll need to track the number of copies we have of each card. It starts at `1`, will go up when previous cards add copies. We'll use a `defaultdict` for that so we can increment without checking membership first:

```py
from collections import defaultdict

...

class Solution(StrSplitSolution):
    def part_1(self) -> int:
        num_copies: defaultdict[int, int] = defaultdict(int)
```

For each card, the N _next_ cards each get a copy for each winner on that card. So we'll count our winners (same as before) and use that as the far end of a `range`:

```py
...

class Solution(StrSplitSolution):
    def part_1(self) -> int:
        num_copies: defaultdict[int, int] = defaultdict(lambda: 1)

        for idx, line in enumerate(self.input):
            card_id = idx + 1  # 1-index our card numbers!

            num_winners = count_winning_numbers(line)

            # start after our current id and go for `num_winners` more cards
            for c in range(card_id + 1, card_id + 1 + num_winners):
                num_copies[c] += 1

        # return the total number of cards
        return sum(num_copies.values())
```

This was on the right track, but didn't solve the example yet. There were 2 bugs:

1. Cards that are never duplicated are never accessed in our `defaultdict`, meaning they're missing from the final total
2. We're not accounting for copied cards (i.e. there are 4 copies of card `3`, so there should be _lots_ of card 4. We're not doing any multiplication yet, which is probably wrong)

Luckily, these are both easy fixes:

```py ins={10} ins="+= num_copies[card_id]" ins="defaultdict(int)"
...

class Solution(StrSplitSolution):
    def part_1(self) -> int:
        num_copies: defaultdict[int, int] = defaultdict(int)

        for idx, line in enumerate(self.input):
            card_id = idx + 1  # 1-index our card numbers!

            num_copies[card_id] += 1
            num_winners = count_winning_numbers(line)

            # start after our current id and go for `num_winners` more cards
            for c in range(card_id + 1, card_id + 1 + num_winners):
                num_copies[c] += num_copies[card_id]

        ...
```

1. When we calculate winners for each card, we count it once. This also simplifies our `defaultdict`, since everything can start at 0.
2. We switched to multiplication! Instead of incrementing by 1, we increment based on the number of copies of the current card.

And that'll do it! These puzzles have been all over the place with the amount of code required, but hey, [puzzle difficulty is tricky](https://old.reddit.com/r/adventofcode/comments/7idn6k/question_why_does_the_difficulty_vary_so_much/dqy08tk/)!
