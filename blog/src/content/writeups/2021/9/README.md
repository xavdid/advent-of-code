---
year: 2021
day: 9
title: "Smoke Basin"
slug: "2021/day/9"
pub_date: "2021-12-09"
---

## Part 1

For this part, I couldn't think of a clever way to do this off the top of my head. So we're going to it the simple way. Our input is a grid, like we've seen before. We'll iterate both directions, look at all neighbors, and check if we're the smallest. The only slightly tricky thing is to be careful checking the sides and corners:

```py
total = 0
for row, line in enumerate(self.input):
    for col, spot in enumerate(line):
        neighbors = []
        if col > 0:
            neighbors.append(line[col - 1])
        if col < len(line) - 1:
            neighbors.append(line[col + 1])

        if row > 0:
            neighbors.append(self.input[row - 1][col])
        if row < len(self.input) - 1:
            neighbors.append(self.input[row + 1][col])
```

Once we've found the neighbors, we can check our spot against it and total it up if it's the smallest one:

```py
for row, line in enumerate(self.input):
    for col, spot in enumerate(line):
        ...

        spot = int(spot)
        if all(spot < int(x) for x in neighbors):
            total += spot + 1

return total
```

It's not pretty, but it works!

## Part 2

Part 2's description comes with an interesting tidbit- each number is only part of a single basin and 9's are excluded. That means for any spot on the grid, we can explore whatever basin we're in. We'll have to keep track of the points we've seen, but should be able to group and separate them easily enough. We'll be able to refactor our part 1 code too; once we've grouped points into basins, it'll be easy to find the minimum value.

As with most grid-based puzzles, I find it helpful to add some helper methods to our solution class. This helps keep our other methods simpler. Here are the two I used:

```py
from typing import List, Set, Tuple

Point = Tuple[int, int]

class Solution(StrSplitSolution):

    def neighbors(self, row: int, col: int) -> List[Point]:
        neighbors: List[Point] = []
        if col > 0:
            neighbors.append((row, col - 1))
        if col < len(self.input[row]) - 1:
            neighbors.append((row, col + 1))

        if row > 0:
            neighbors.append((row - 1, col))
        if row < len(self.input) - 1:
            neighbors.append((row + 1, col))

        return [n for n in neighbors if self.value_at(*n) != 9]

    def value_at(self, row: int, col: int) -> int:
        return int(self.input[row][col])
```

That first one should look familiar - it's most of our code from part 1. The only change is the filtering of 9s at the end - they're not part of basins, so we can basically ignore them for this puzzle.

The rest is a common algorithm called [Depth First Search](https://en.wikipedia.org/wiki/Depth-first_search). We look at a point. If we haven't seen it before, we log it, then add all its neighbors to the to-look list. Once that list is empty, we've seen everything in the basin and can do our calculations. We start with some setup and variables:

```py
total = 0
basins: List[Set[Point]] = []
all_points: Set[Point] = set()

for row in range(len(self.input)):
    for col in range(len(self.input[0])):
        loc = (row, col)
        if loc in all_points or self.value_at(*loc) == 9:
            continue
```

This loop will spend a lot of time skipping. It's here to get us to our next (or first) basin. Once we found one, we explore it!

```py
for row in range(len(self.input)):
    for col in range(len(self.input[0])):
        ...

        # explore this basin
        to_explore = [loc]
        basin: Set[Point] = set()
        while to_explore:
            p = to_explore.pop()
            if p not in basin:
                basin.add(p)
                to_explore += self.neighbors(*p)
```

The only trick here is the reappearance of Python's "spread operator" (previously discussed on [day 3](/writeups/2021/day/3/)). Since `self.neighbors` takes `row, col`, I could either:

- split out the point: `self.neighbors(p[0], p[1])`
- use `*` to tell Python to split this tuple into multiple arguments: `self.neighbors(*p)`

The second felt much cleaner. The function could have also been written to take a `Point`, but I wanted it to be consistent with `neighbors`, so here we are.

Anyway, when that `while` loop finishes, we should have a `basin` made of points. We'll add the `min` for part 1, then add it to our list of basins and its points to our `all_points` so it's ignored when looking for our next basin:

```py
for row in range(len(self.input)):
    for col in range(len(self.input[0])):
        ...

        total += min(self.value_at(*p) for p in basin) + 1
        all_points.update(basin)
        basins.append(basin)
```

Our `for` loop keeps finding basins and exits eventually. All that's left is to sort our list of basins, multiply their sizes, and return our answer for both parts:

```py
big_basins = sorted(basins, key=len, reverse=True)[:3]
basin_product = len(big_basins[0]) * len(big_basins[1]) * len(big_basins[2])

return total, basin_product
```

`sorted` is a funny method in Python. It takes an iterable, plus a `key`, which should be a function that takes a single argument (such as `len`). It sorts the item based on their result from that function. Super useful here for getting the largest basins to the front of our list.

Good job so far! You're now more than 1/3 the way to Christmas!
