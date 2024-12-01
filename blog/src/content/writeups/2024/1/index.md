---
year: 2024
day: 1
slug: "2024/day/1"
title: "Historian Hysteria"
# concepts: []
pub_date: "2024-11-30"
---

Welcome once again to [Advent of Code](https://adventofcode.com/)! Over the next 25 blog posts, we'll be walking through step-by-step solutions to each of this year's puzzles in modern, idiomatic Python.

There are a few goals:

- improve understanding of what's available in the Python standard library
- produce clear, readable code
- get comfortable with non-trivial programming concepts

Readers are [expected to have](https://advent-of-code.xavd.id/#audience) a basic understanding of programming fundamentals. Advent of Code isn't the place to learn programming from scratch ([Exercism's upcoming bootcamp](https://bootcamp.exercism.org/) is a better place for that).

Each of my solutions will use my [GitHub template](https://github.com/xavdid/advent-of-code-python-template), which handles some basic input parsing. It also a good [Ruff](https://docs.astral.sh/ruff/) setup for linting and formatting. Feel free to fork this an adapt it for your needs! I didn't include any utility functions in the template itself, but you're encouraged to write and use your own. I've got a few (like for graph traversal) that I'll reference in my solutions, but you can take whatever approach you'd like.

I think that's everything. Let's get to it!

## Part 1

We'll start today like we will most days, by parsing our input. We're given a pair of vertical looking lists that we'll have to move through a line at a time. There may be a more elegant way to do it, but we can make a couple of lists and add to them as we go:

```py
class Solution(StrSplitSolution):
    def part_1(self) -> int:
        l, r = [], []

        for line in self.input:
            a, b = line.split()
            l.append(int(a))
            r.append(int(b))
```

Rough, but readable. Next, we need to sort these lists since we'll be comparing the Nth elements of each:

```py
class Solution(StrSplitSolution):
    def part_1(self) -> int:
        ...

        l.sort()
        r.sort()
```

Python can sort lists of ints in place, so that's a freebie.

Lastly, we need to compare each element of the left list with its match on the right. The `zip` function is perfect for this! `zip([1, 2, 3], [4, 5, 6])` produces `[(1, 4), (2, 5), (3, 6)]`, which is exactly how we want to group our sorted lists.

Iterating over those zipped lists and summing the absolute value of the differences gives our answer for part 1:

```py
class Solution(StrSplitSolution):
    def part_1(self) -> int:
        ...

        return sum(abs(a - b) for a, b in zip(l, r))
```

### A More Elegant Approach?

The best and worst thing about Python is that it lets you write very dense code. But, that code can be harder to read an reason about, even if it does the same thing in fewer lines.

For instance, another way to parse our input is as follows:

```py rem={3-9} ins={10-11}
class Solution(StrSplitSolution):
    def part_1(self) -> int:
        l, r = [], []
        for line in self.input:
            a, b = line.split()
            l.append(int(a))
            r.append(int(b))
        l.sort()
        r.sort()
        pairs = [map(int, l.split()) for l in self.input]
        l, r = [sorted(col) for col in zip(*pairs)]
```

The first line iterates over the input and calls `int()` on each item in the split row (each of our 2 numbers). The next one combines:

1. the `*` operator to pass each element of a list of pairs to `zip`, which groups the 1st and 2nd elements of each into big tuples
2. the `sorted` function in a list comprehension, which returns a sorted list version of those tuples

Which version do you prefer? Which would you rather stumble upon in an old corner of the codebase? I find the second manageable enough, especially if I can hide it in a (well-tested) utility function. But, to each their own!

## Part 2

Next, we need to know how many times each number from the left column appears in the right one. Luckily, Python's [collections.Counter](https://docs.python.org/3/library/collections.html#collections.Counter) is perfect for this! It takes an iterable and counts the occurrence of each element, storing the result in a dict-like structure. The counted version of the right list shows:

```py
from collections import Counter

c = Counter(r) # r is the right list
# => Counter({3: 3, 4: 1, 5: 1, 9: 1})
```

Each key is an element and its value is the number of times it occurs. That's all we need to iterate over our left list:

```py rem={4,8} ins={1,5,9,11-12,14}
from collections import Counter

class Solution(StrSplitSolution):
    def part_1(self) -> int:
    def solve(self) -> tuple[int, int]:
        ... # part 1 code

        return sum(abs(a - b) for a, b in zip(l, r))
        total_distance = sum(abs(a - b) for a, b in zip(l, r))

        c = Counter(r)
        similarity_score = sum(i * c.get(i, 0) for i in l)

        return total_distance, similarity_score
```

`Counter` has the same `.get(key, default)` interface that a `dict` does. That, with another small list comprehension, gets us over the line. 2 down, 48 to go!
