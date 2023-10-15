---
year: 2020
day: 5
title: "Binary Boarding"
slug: "2020/day/5"
pub_date: "2020-12-05"
---

## Part 1

In case you weren't clued in from the puzzle's title, today is a twist on a [binary search](https://en.wikipedia.org/wiki/Binary_search_algorithm). Given a sorted list, you cut in in half, test where your target element is (higher or lower than the midpoint), and throw out the other set. Do this enough times and you quickly find the index of the element you're searching for. A binary search is efficient because you only need to check a few elements to find the target (as compared to a "linear" search, where you check every element until the target is found). The AoC twist is that we don't _have_ a target value. Instead, we use `char`s to decide which half of the results to keep.

Off the bat, we know we'll be doing a loop a fixed number of times (7 characters). The function that takes that length-7 string will return a row number, so we can start there:

```py
def find_row(instructions: int) -> int:
    for c in instructions:
        pass # TBD
```

Normally when searching a list it's expected that you have the whole list to search through. One way to start this is by creating such a list using Python's `range` function: `list(range(127))` (which gives `[0, 1, 2, ... 127]`). But, because we know exactly what the contents of the range are, we can skip initializing the list entirely! We just do the same math we'd do in a normal binary search, but on the numbers themselves instead of list elements.

Given that, we can do a pretty standard binary search:

```py
from math import floor

def find_row(instructions: int) -> int:
    low = 0
    high = 127
    mid = floor((high + low) / 2)
    for c in instructions:
        # print(low, high) # very helpful for visualizing each step
        if c == "F":
            # bottom half
            high = mid
            mid = get_midpoint(low, high)
        else:
            # top half
            low = mid + 1
            mid = get_midpoint(low, high)

    return mid
```

Moving on to the second segment, the description looks awfully similar - we're doing a binary search again, but with only 3 loops on 8 numbers. Given that, we can adapt our function to do both row and seat by taking `high` as a parameter and checking both letters that mean "bottom half":

```py
def binary_search(instructions: int, high: int) -> int:
    low = 0
    high = top
    mid = floor((high + low) / 2)
    for c in instructions:
        if c in ("F", "L"):
            # bottom half
            high = mid
            mid = get_midpoint(low, high)
        else:
            # top half
            low = mid + 1
            mid = get_midpoint(low, high)

    return mid
```

Now that that's easy to call, we get the value for each ticket and return the max:

```py
def calulate_score(assignment: str) -> int:
    return (binary_search(assignment[:7], 127) * 8) + binary_search(assignment[7:], 7)

return max([calulate_score(assignment) for assignment in self.input])
```

## Part 2

From my read of this question, it sounds like the seat IDs will be a continuous run of numbers, but not one that starts at 0. We need to find the number that's missing from the range.

Our answer from part 1 is the high end of the number range (using `max`). If we pair that with the `min`, we'll know both bounds of our range. If we have the full range and the range-without-a-number, we can subtract the two as sets and only the missing number will be left.

> Note that this function uses the Python quickhand for creating sets, which looks creating a dict, but without keys.

```py
seat_ids = {calulate_score(assignment) for assignment in self.input}

full_range = set(range(min(seat_ids), max(seat_ids)))

return (full_range - seat_ids).pop()
```
