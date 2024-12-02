---
year: 2024
day: 2
slug: "2024/day/2"
title: "Red-Nosed Reports"
# concepts: []
pub_date: "2024-12-02"
---

## Part 1

Our main goal today is to decide if a list of ints is "safe", meaning it's strictly increasing (or decreasing) and doesn't jump too far in a single step.

The stdlib function `iterools.pairwise` lets us iterate over every adjacent pair of elements in the list, which is perfect for our needs:

```py
from itertools import pairwise

list(pairwise([2,4,6,8,10]))
# => [(2, 4), (4, 6), (6, 8), (8, 10)]
```

For each of those pairs, we want to ensure it follows both of the rules:

1. the left item is strictly less than the right one
2. the difference between right and left is between `1` and `3` (inclusive)

Python's global `all` function will tell us whether that condition is true for _all_ possible pairs, which is exactly what we need! It'll also exit as soon as a pair fails the check, so it's pretty cheap to run.

Past that, encoding the rules is simple:

```py
from itertools import pairwise

def is_strictly_increasing(vals: list[int]) -> bool:
    return all(l < r and 1 <= r - l <= 3 for l, r in pairwise(vals))
```

This only works to test strictly increasing lists, but we have to account for strictly decreasing ones too. We could write an inverse version of our check (i.e. `r < l and ...`), but there's a better way.

Because a valid decreasing list is just a valid increasing list in reverse, we can pass each input forward and backward to our function to determine safety:

```py
...

def is_safe(vals: list[int]) -> bool:
    return is_strictly_increasing(vals) or is_strictly_increasing(vals[::-1])
```

> `vals[::-1]` reverses `vals` using a classic Python trick. Python slices (the numbers and colons in square brackets) take `[start : stop : step]` as their 3 arguments. Anything missing uses the default value. `step` defaults to `1` (to step forward through a list one element at a time), which is how it's typically used. Here, we specify a `step` of `-1` to walk backwards (and retain the default start and end locations), which reverses our list!

To actually solve the puzzle, we have to run every line in the input through `is_safe` and count them. Each line gets parsed into a list of `int`s before going in:

```py
...

class Solution(StrSplitSolution):
    def part_1(self) -> int:
        return sum(is_safe([int(e) for e in line.split()]) for line in self.input)
```

Being able to `sum` a list of `bool`s is convenient! It's a side effect of Python's `bool` inheriting from `int`, so you can treat them like numbers:

```py
True + True
# => 2
True + False
# => 1
```

## Part 2

Now we have to determine if any inputs are 1 rogue element away from being valid. If a line isn't safe on its own, we'll remove one element at a time and try that instead. If any of _those_ pass, then the line would be safe for the purposes of part 2.

The only extra code we need here is an easy way to get all of the "dampened" versions of a list. We'll use a generator, which is a memory-efficient way to create an iterable on-demand (instead of pre-computing everything). All that needs is the `yield` keyword in place of `return`:

```py
from typing import Iterable
...

def omit_one(vals: list[int]) -> Iterable[list[int]]:
    for idx in range(len(vals)):
        yield vals[:idx] + vals[idx + 1 :]
```

For each element, we'll get everything up to and after that index, omitting one spot at a time.

Combine that with a small tweak to part 1 and we're off ot the races:

```py
...

class Solution(StrSplitSolution):
    def part_2(self) -> int:
        lists = [parse_int_list(line.split()) for line in self.input]

        return sum(is_safe(l) or any(is_safe(o) for o in omit_one(l)) for l in lists)
```
