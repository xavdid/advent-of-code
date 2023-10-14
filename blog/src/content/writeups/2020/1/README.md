---
year: 2020
day: 1
title: "Report Repair"
slug: "2020/day/1"
pub_date: "2020-12-01"
---

## Part 1

The best season is finally upon us! It's Advent of Code time. Luckily, we start on a straightforward note.

We're looking for a sum of 2020, so for each item in the list, we know exactly what our matching number will be. So, we can iterate through the list and return the result when we find the match:

```py
for amount in self.input:
    target = 2020 - amount
    if target in self.input:
        return amount * target
```

The above uses `self.input` from the helper class in this repo, so your code will look a little different than mine, but the core idea is the same.

This could be sped up by removing the `target in self.input` call, which has to look through the whole list every time. But, Python is fast and the program completed basically instantly, so I'm not worried about it.

## Part 2

This looks a lot like part 1, but we need to look at each pair of numbers in the list and see if their third is present. Luckily, Python has a method that will do the hard part for us: `itertools.combinations`. It takes an iterable (aka anything that can be iterated over) and returns every possible pair of items. From [the docs](https://docs.python.org/3/library/itertools.html#itertools.combinations):

```py
from itertools import combinations
list(combinations('ABCD', 2))
# [('A', 'B'), ('A', 'C'), ('A', 'D'), ('B', 'C'), ('B', 'D'), ('C', 'D')]
```

Order doesn't matter, so `('B', 'A')` isn't in the list (it's the same as `('A', 'B')`).

This lets us write basically the same loop from part 1 where we know exactly what number we need each time:

```py
for a, b in combinations(self.input, 2):
    target = 2020 - a - b
    if target in self.input:
        return a * b * target
```
