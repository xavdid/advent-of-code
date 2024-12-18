---
year: 2024
day: 11
slug: "2024/day/11"
title: "Plutonian Pebbles"
# concepts: []
pub_date: "2024-12-17"
---

## Part 1

For each item in our list, we need to replace it with 1 or 2 items. We could do a mix of `.append()` and `.extend()` depending on the `if` branch, but maintainability wise, that's a little messy. Instead, let's abstract the computation into a function that always returns a list, then flatten that out in the main function.

Our actual computation is simple:

```py
def step_stone(s: str) -> list[str]:
    if s == "0":
        return ["1"]

    if (l := len(s)) % 2 == 0:
        cut_line = l // 2
        return [str(int(new_stone)) for new_stone in (s[:cut_line], s[cut_line:])]

    return [str(int(s) * 2024)]
```

We're working with strings because we need to know how many digits the number is and be able to split it as a string.

For the actual computation, we map that function over our input and use the `iterools.chain.from_iterable` [trick from day 9](/writeups/2024/day/9/) to turn our lists, however long they are, into a single iterable (ready to be mapped over again):

```py
...

class Solution(StrSplitSolution):
    separator = " " # split on spaces instead of newlines

    def part_1(self) -> int:
        stones = self.input

        for _ in range(25):
            stones = chain.from_iterable(map(step_stone, stones))

        return len(list(stones))
```

We need an explicit `list` call at the end because the type returned from `chain` is an [iterable](https://docs.python.org/3/library/stdtypes.html#iterator-types), but not a [sequence](https://docs.python.org/3/library/stdtypes.html#sequence-types-list-tuple-range)- it has no length until fully explored.

I liked this part as an example of when complicating an operation (adding lists where we don't otherwise need them) simplifies everything else (only a single case to handle in `part_1`, so we can streamline the whole thing).

## Part 2

This is a classic Advent of Code move: a puzzle that's easy after a few steps and impossible after more. Because of the rate at which the length of the array grows, we can't simulate the whole thing. We'll have to adjust our approach.

At first, I thought there'd be some sort of cycle that would allow us to extrapolate. There sort of is- a `0` will always go through the same transformations (with arrays around the :

```
0
1
2024
20 24
2 0 2 4
4048 1 4048 8096
40 48 2024 40 48 80 96
4 0 4 8 20 24 4 0 4 8 8 0 9 6
```

Every time there's a `0`, 4 steps later, it'll be a `2 0 2 4`, which will repeat the process, plus similar patterns for the other numbers (which will spawn more `0`s in turn). We could probably math out the grown, but there's an easier way.

Despite the phrase `order is preserved` being **bolded** in the instructions, the order of the stones doesn't _actually_ matter. We need to know how many stones there are total, but nothing about the way they transform cares about their neighbors. Furthermore, each instance of a number transforms the same way: every `0` will become a `1`. So we don't really have to handle each one individually...

With those two facts in mind, we could store our stones in a `dict` where the keys are the stone and the value is the number of times that stone appears in our collection. Turning a bunch of `0`s into a bunch of `1`s is as easy as storing the old value under a new key:

```py
from collections import defaultdict

...

class Solution(StrSplitSolution):
    ...

    def part_2(self) -> int:
        stones: dict[str, int] = {k: 1 for k in self.input}
        assert len(stones) == len(self.input)

        for _ in range(75):
            new_stones = defaultdict(int)
            for stone, num in stones.items():
                for new_stone in step_stone(stone):
                    new_stones[new_stone] += num

            stones = new_stones

        return sum(stones.values())
```

We could also use a `collections.Counter` for our initial `self.input`, but since each number appears only once, a simple dict is just as good. From there, the rest of it runs like a breeze (upto any number!).
